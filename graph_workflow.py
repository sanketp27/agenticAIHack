import os
import json
import re
from typing import Dict, Any, List, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from google import genai
from google.genai import types
from langgraph.graph import StateGraph, END
from datetime import datetime, timedelta

class TravelPlannerState(TypedDict):
    """State for the travel planner workflow"""
    user_input: str
    session_id: str
    clarification_needed: bool
    clarification_questions: List[str]
    trip_preferences: Dict[str, Any]
    itinerary_toc: Dict[str, Any]  # Table of Contents for itinerary generation
    success_criteria: List[str]
    data_quality_requirements: List[str]
    itinerary: Dict[str, Any]
    final_response: str
    conversation_history: List[str]

# Get environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")

class TravelPlannerGraph:
    """Multi-agent travel planner using LangGraph"""
    
    def __init__(self):
        self.client = self._configure_gemini()
        self.workflow = self._build_workflow()
        self._initialize_tools()

    def _configure_gemini(self):
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        client = genai.Client(api_key=GOOGLE_API_KEY)
        return client
    
    def _initialize_tools(self):
        grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )

        self.config = types.GenerateContentConfig(
            tools=[grounding_tool]
        )
     
    def _build_workflow(self) -> StateGraph:
        """Build the workflow graph"""
        workflow = StateGraph(TravelPlannerState)
        
        workflow.add_node("clarifying_agent", self._clarifying_agent)
        workflow.add_node("root_agent", self._root_agent)
        workflow.add_node("itinerary_agent", self._itinerary_agent)
        workflow.add_node("response", self._response_agent)
        
        workflow.set_entry_point("clarifying_agent")
        
        workflow.add_conditional_edges(
            "clarifying_agent",
            self._should_clarify,
            {
                "clarify": END, 
                "continue": "root_agent"
            }
        )
        
        workflow.add_edge("root_agent", "itinerary_agent")
        workflow.add_edge("itinerary_agent", "response")
        workflow.add_edge("response", END)
        
        return workflow.compile()
    
    def _clarifying_agent(self, state: TravelPlannerState) -> TravelPlannerState:
        """Agent to clarify user requirements"""
        user_input = state["user_input"]
        
        prompt = f"""
        You are a travel clarification agent. Analyze the user's travel request and determine if you have enough information to plan a trip.

        User input: "{user_input}"
        
        Required information for trip planning:
        1. Destination (city/country)
        2. Travel dates or duration
        3. Budget (at least a range)
        4. Number of travelers
        5. Accommodation preference (budget/mid/premium/luxury)
        6. Main interests (culture, food, adventure, nightlife, etc.)
        7. Trip pace (relaxed, balanced, packed)
        8. Origin/departure location

        Note:
        Return the response in given format only.
        Do not return any free flowing text

        If any critical information is missing, respond with:
        {{
            "clarification_needed": true,
            "questions": ["specific question 1", "specific question 2", ...],
            "message": "I'd like to help you plan the perfect trip! I need a few more details to get started."
        }}

        If you have enough information, respond with:
        {{
            "clarification_needed": false,
            "preferences": {{extracted and organized trip preferences}},
            "message": "Great! I have all the information needed to plan your trip."
        }}
        
        Be concise and ask only the most essential missing questions (max 3-4 questions).
        """
   
        response = self.client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=self.config,
        )
        
        try:
            result = json.loads(response.text)
            
            if result.get("clarification_needed"):
                state["clarification_needed"] = True
                state["clarification_questions"] = result.get("questions", [])
                state["final_response"] = result.get("message", "I need more information to plan your trip.")
            else:
                state["clarification_needed"] = False
                state["trip_preferences"] = result.get("preferences", {})
                state["final_response"] = result.get("message", "Ready to plan your trip!")
                
        except json.JSONDecodeError:
            # Fallback logic
            if any(keyword in response.text.lower() for keyword in ["need", "missing", "clarify", "more information"]):
                state["clarification_needed"] = True
                state["clarification_questions"] = ["Could you provide more details about your destination and travel dates?"]
                state["final_response"] = "I need a bit more information to plan your perfect trip."
            else:
                state["clarification_needed"] = False
                state["trip_preferences"] = {}
        
        state["conversation_history"].append(f"User: {user_input}")
        return state
    
    def _should_clarify(self, state: TravelPlannerState) -> str:
        return "clarify" if state["clarification_needed"] else "continue"
    
    def _root_agent(self, state: TravelPlannerState) -> TravelPlannerState:
        """Root agent to validate and enrich trip preferences"""
        preferences = state["trip_preferences"]
        
        prompt = f"""
        You are a travel planning root agent. Your task is to validate trip preferences and generate a comprehensive Table of Contents (TOC) that will guide the Itinerary Multi-Agent System to fetch real-time data and create detailed travel plans.

        Current preferences:
        {preferences}

        Your responsibilities:
        1. Validate and enrich trip preferences with reasonable defaults
        2. Generate a detailed TOC/action plan for the Itinerary Multi-Agent System
        3. Specify which sub-agents and tools should be activated
        4. Define data collection priorities and sequence

        Return a JSON object with the following structure:
        {{
            "validated_preferences": {{
                "traveler_name": "traveler name or 'Traveler'",
                "origin": "departure location",
                "destination": "destination",
                "start_date": "YYYY-MM-DD",
                "end_date": "YYYY-MM-DD", 
                "duration_days": "number",
                "budget_total": "number",
                "budget_per_day": "number",
                "travelers_count": "number",
                "accommodation_tier": "budget/mid/premium/luxury",
                "interests": ["interest1", "interest2"],
                "pace": "relaxed/balanced/packed",
                "special_requirements": ["any special needs"],
                "destination_context": "brief context about destination"
            }},
            "success_criteria": [
                "All activities align with stated interests",
                "Total cost within 10% of budget",
                "Realistic time allocations for each activity"
            ],
            "data_quality_requirements": [
                "Real-time pricing where possible",
                "Current operating hours and availability"
            ]
        }}
        """
        
        response = self.client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=self.config,
        )
        
        try:
            toc_result = json.loads(response.text)
            # Extract validated preferences and TOC
            state["trip_preferences"] = toc_result.get("validated_preferences", preferences)
            state["success_criteria"] = toc_result.get("success_criteria", [])
            state["data_quality_requirements"] = toc_result.get("data_quality_requirements", [])
        except json.JSONDecodeError:
            # Keep existing preferences if parsing fails
            pass
            
        state["conversation_history"].append("Root Agent: Trip preferences validated")
        return state
    
    def _itinerary_agent(self, state: TravelPlannerState) -> TravelPlannerState:
        """Agent to generate detailed itinerary"""
        preferences = state["trip_preferences"]
        
        prompt = f"""
        You are an expert travel itinerary agent. Create a detailed, day-by-day itinerary based on the preferences.

        Trip Preferences:
        {json.dumps(preferences, indent=2)}

        Create a comprehensive itinerary with:
        1. Daily schedule (morning, afternoon, evening activities)
        2. Accommodation recommendations
        3. Transportation between activities
        4. Meal recommendations
        5. Budget breakdown
        6. Local tips and insights
        7. Alternative options for weather/preferences

        Return a JSON object with this structure:
        {{
            "summary": "brief trip overview",
            "total_estimated_cost": "number",
            "accommodation": {{
                "recommendation": "hotel/area name",
                "tier": "tier level",
                "nightly_rate": "number",
                "total_nights": "number",
                "total_cost": "number"
            }},
            "daily_itinerary": [
                {{
                    "day": 1,
                    "date": "YYYY-MM-DD",
                    "theme": "day theme",
                    "morning": {{
                        "activity": "activity name",
                        "location": "location",
                        "duration": "duration",
                        "cost": "number",
                        "tips": "helpful tips"
                    }},
                    "afternoon": {{"activity": "activity", "location": "location", "cost": "number"}},
                    "evening": {{"activity": "activity", "location": "location", "cost": "number"}},
                    "meals": {{
                        "breakfast": "recommendation",
                        "lunch": "recommendation", 
                        "dinner": "recommendation"
                    }},
                    "transportation": "how to get around",
                    "daily_budget": "number"
                }}
            ],
            "budget_breakdown": {{
                "accommodation": "number",
                "activities": "number",
                "food": "number",
                "transportation": "number",
                "total": "number"
            }},
            "packing_list": ["item1", "item2"],
            "local_tips": ["tip1", "tip2"]
        }}

        Make it detailed, practical, and tailored to their interests and budget.
        """
        
        response = self.client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=self.config,
        )
        
        try:
            itinerary = json.loads(response.text)
            state["itinerary"] = itinerary
        except json.JSONDecodeError:
            # Create a basic fallback itinerary
            state["itinerary"] = self._create_fallback_itinerary(preferences)
            
        state["conversation_history"].append("Itinerary Agent: Detailed itinerary created")
        return state
    
    def _response_agent(self, state: TravelPlannerState) -> TravelPlannerState:
        """Final response agent to format the output"""
        preferences = state["trip_preferences"]
        itinerary = state["itinerary"]
        
        prompt = f"""
        You are a travel concierge agent. Create a friendly, engaging response for the traveler with their complete trip plan.

        Trip Preferences:
        {json.dumps(preferences, indent=2)}

        Itinerary:
        {json.dumps(itinerary, indent=2)}

        Create a warm, personalized response that includes:
        1. Enthusiastic greeting and trip summary
        2. Highlight of key experiences aligned with their interests
        3. Budget summary and value highlights
        4. Next steps and booking recommendations
        5. Offer for modifications or questions

        Keep it conversational, exciting, and under 300 words. Focus on making them excited about their trip!
        """
        
        response = self.client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=self.config,
        )
        
        state["final_response"] = response.text
        state["conversation_history"].append("Response Agent: Final response prepared")
        
        return state
    
    def _create_fallback_itinerary(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Create a basic fallback itinerary if JSON parsing fails"""
        destination = preferences.get("destination", "Your destination")
        duration = preferences.get("duration_days", 5)
        budget = preferences.get("budget_total", 1500)
        
        return {
            "summary": f"A {duration}-day trip to {destination}",
            "total_estimated_cost": budget,
            "daily_itinerary": [
                {
                    "day": i,
                    "theme": f"Day {i} exploration",
                    "activities": "Customized activities based on your interests",
                    "daily_budget": budget // duration if duration > 0 else 300
                }
                for i in range(1, duration + 1)
            ],
            "local_tips": ["Stay hydrated", "Try local cuisine", "Learn basic local phrases"],
            "packing_list": ["Comfortable walking shoes", "Weather-appropriate clothing", "Travel documents"],
            "budget_breakdown": {
                "accommodation": budget * 0.4,
                "activities": budget * 0.3,
                "food": budget * 0.2,
                "transportation": budget * 0.1,
                "total": budget
            }
        }