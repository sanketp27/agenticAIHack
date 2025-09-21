import os
import json
from typing import Dict, List, Any, TypedDict, Annotated
from dotenv import load_dotenv
import google.generativeai as genai
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
import requests
from datetime import datetime


load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


class TripPreferences(BaseModel):
    """Pydantic model for trip preference structure"""
    traveler_name: str = Field(description="Traveler full name")
    origin: str = Field(description="Departure city/airport")
    destination: str = Field(description="Target city/country or multi-city list")
    start_date: str = Field(description="Trip start date (YYYY-MM-DD)")
    end_date: str = Field(description="Trip end date (YYYY-MM-DD)")
    budget_total: float = Field(description="Total trip budget in local currency")
    interests: List[str] = Field(description="Interests like culture, nightlife, food, adventure")
    travelers_count: int = Field(description="Number of travelers")
    accommodation_tier: str = Field(description="Preferred tier: budget, mid, premium, luxury")
    pace: str = Field(description="Trip pace: relaxed, balanced, packed")


class TripPlanningState(TypedDict):
    """State for the personalized trip planning workflow"""
    traveler_name: str
    preferences: Dict[str, Any]
    constraints: Dict[str, Any]
    destination_data: Dict[str, Any]
    itinerary: Dict[str, Any]
    recommendations: List[str]
    budget_fit_score: float
    booking_details: Dict[str, Any]
    payment_receipt: Dict[str, Any]
    messages: Annotated[List[BaseMessage], add_messages]


class TravelOrchestrationAgent:
    """Central orchestration agent for AI-powered personalized trip planning"""

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-latest",
            temperature=0.2,
            max_tokens=2048,
            google_api_key="AIzaSyB2RgPrXYpJ7B55eYZl83BL2xrrfhQd7P8"
        )
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for personalized trip planning"""
        workflow = StateGraph(TripPlanningState)

        # Add nodes for each step
        workflow.add_node("preference_collector", self._preference_collection_agent)
        workflow.add_node("destination_data", self._destination_data_agent)
        workflow.add_node("itinerary_generator", self._itinerary_generation_agent)
        workflow.add_node("budget_optimizer", self._budget_optimization_agent)
        workflow.add_node("realtime_adapter", self._real_time_adjustment_agent)
        workflow.add_node("booking_agent", self._booking_agent)
        workflow.add_node("payment_agent", self._payment_agent)
        workflow.add_node("insight_generator", self._insight_generation_agent)

        # Define the workflow edges
        workflow.set_entry_point("preference_collector")
        workflow.add_edge("preference_collector", "destination_data")
        workflow.add_edge("destination_data", "itinerary_generator")
        workflow.add_edge("itinerary_generator", "budget_optimizer")
        workflow.add_edge("budget_optimizer", "realtime_adapter")
        workflow.add_edge("realtime_adapter", "booking_agent")
        workflow.add_edge("booking_agent", "payment_agent")
        workflow.add_edge("payment_agent", "insight_generator")
        workflow.add_edge("insight_generator", END)

        return workflow.compile()

    def _preference_collection_agent(self, state: TripPlanningState) -> TripPlanningState:
        """Collect and normalize traveler preferences and constraints"""
        preferences = state["preferences"]
        normalized = self._collect_user_preferences(preferences)
        state["preferences"] = normalized
        state["constraints"] = {
            "budget_total": preferences.get("budget_total"),
            "dates": {
                "start": preferences.get("start_date"),
                "end": preferences.get("end_date")
            },
            "travelers_count": preferences.get("travelers_count", 1)
        }

        state["messages"].append(AIMessage(content=f"Preferences collected for {state['traveler_name']}"))
        return state

    def _destination_data_agent(self, state: TripPlanningState) -> TripPlanningState:
        """Gather destination data: attractions, transit, weather, events, prices"""
        destination = state["preferences"].get("destination")
        destination_data = self._collect_destination_data(destination)
        state["destination_data"] = destination_data
        state["messages"].append(AIMessage(content=f"Destination data gathered for {destination}"))
        return state

    def _itinerary_generation_agent(self, state: TripPlanningState) -> TripPlanningState:
        """Generate a draft end-to-end itinerary with activities, lodging, and transport"""
        preferences = state["preferences"]
        data = state["destination_data"]

        prompt = f"""
        You are an AI trip planner. Create a daily, end-to-end itinerary.
        Preferences:
        {json.dumps(preferences, indent=2)}

        Destination data:
        {json.dumps(data, indent=2)}

        Output a JSON with keys: days (array per day with morning/afternoon/evening activities, transport, meals),
        lodging (with area, tier, nightly_estimate), intra_city_transport, total_estimated_cost, and rationale.
        Respect budget, dates, interests (e.g., culture, nightlife, adventure), and trip pace.
        """

        response = self.llm.invoke(prompt)
        itinerary = self._generate_itinerary_from_llm(response.content)
        state["itinerary"] = itinerary
        state["messages"].append(AIMessage(content="Draft itinerary generated"))
        return state

    def _budget_optimization_agent(self, state: TripPlanningState) -> TripPlanningState:
        """Refine itinerary for best budget fit without sacrificing core interests"""
        itinerary = state["itinerary"]
        budget_total = state["constraints"].get("budget_total")
        optimized, score = self._optimize_budget(itinerary, budget_total)
        state["itinerary"] = optimized
        state["budget_fit_score"] = score
        state["messages"].append(AIMessage(content=f"Budget optimized. Fit score: {score:.2f}"))
        return state

    def _real_time_adjustment_agent(self, state: TripPlanningState) -> TripPlanningState:
        """Adjust itinerary for real-time conditions (weather, closures, events)"""
        destination = state["preferences"].get("destination")
        updates = self._fetch_real_time_updates(destination)
        # Apply simple adjustments
        if updates.get("advisory"):
            state["itinerary"].setdefault("notes", []).append(updates["advisory"])
        state["messages"].append(AIMessage(content="Real-time adjustments applied"))
        return state

    def _booking_agent(self, state: TripPlanningState) -> TripPlanningState:
        """Simulate seamless booking via EaseMyTrip inventory"""
        itinerary = state["itinerary"]
        traveler_name = state["traveler_name"]
        booking = self._book_itinerary_easemytrip(itinerary, traveler_name)
        state["booking_details"] = booking
        state["messages"].append(AIMessage(content="Itinerary reserved via EaseMyTrip (simulated)"))
        return state

    def _payment_agent(self, state: TripPlanningState) -> TripPlanningState:
        """Simulate payment processing and confirmation"""
        booking = state.get("booking_details", {})
        receipt = self._process_payment(booking)
        state["payment_receipt"] = receipt
        state["messages"].append(AIMessage(content="Payment processed (simulated)"))
        return state

    def _insight_generation_agent(self, state: TripPlanningState) -> TripPlanningState:
        """Generate final traveler-facing itinerary summary and recommendations"""
        preferences = state["preferences"]
        itinerary = state["itinerary"]
        booking = state.get("booking_details", {})
        receipt = state.get("payment_receipt", {})

        prompt = f"""
        Create a concise trip memo for the traveler based on preferences and finalized itinerary.
        Preferences:
        {json.dumps(preferences, indent=2)}
        Itinerary:
        {json.dumps(itinerary, indent=2)}
        Booking:
        {json.dumps(booking, indent=2)}
        Payment:
        {json.dumps(receipt, indent=2)}

        Include executive summary, key highlights aligned to interests, budget summary, and next steps.
        Limit to 200 words.
        """

        response = self.llm.invoke(prompt)
        state["recommendations"] = self._generate_recommendations(response.content)
        state["messages"].append(AIMessage(content="Final itinerary and memo generated"))
        # Persist the memo alongside itinerary for caller convenience
        state.setdefault("itinerary", {}).update({"memo": response.content})
        return state

    def _collect_user_preferences(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize and enrich preferences with defaults"""
        defaults = {
            "travelers_count": 1,
            "accommodation_tier": "mid",
            "pace": "balanced",
            "interests": ["culture", "food"],
        }
        normalized = {**defaults, **preferences}
        return normalized

    def _collect_destination_data(self, destination: str) -> Dict[str, Any]:
        """Simulate destination data collection"""
        return {
            "destination": destination,
            "popular_areas": ["City Center", "Old Town", "Waterfront"],
            "attractions": [
                {"name": "Historic Museum", "category": "culture", "avg_cost": 20},
                {"name": "Night Market", "category": "food", "avg_cost": 15},
                {"name": "Skyline Bar", "category": "nightlife", "avg_cost": 30},
                {"name": "Hiking Trail", "category": "adventure", "avg_cost": 0}
            ],
            "weather_forecast": "Mild, occasional showers",
            "event_calendar": ["Food Festival", "Local Concert"],
            "price_index": {"meals": 25, "transport": 10, "lodging_mid": 120}
        }

    def _generate_itinerary_from_llm(self, content: str) -> Dict[str, Any]:
        """Parse LLM output, fallback to a reasonable skeleton if not valid JSON"""
        try:
            return json.loads(content)
        except Exception:
            return {
                "days": [
                    {"day": 1, "morning": ["City walking tour"], "afternoon": ["Museum"], "evening": ["Night market"]}
                ],
                "lodging": {"area": "City Center", "tier": "mid", "nightly_estimate": 120},
                "intra_city_transport": "Metro and rideshare",
                "total_estimated_cost": 800,
                "rationale": "Balanced culture and food focus"
            }

    def _optimize_budget(self, itinerary: Dict[str, Any], budget_total: float) -> (Dict[str, Any], float):
        """Simple budget optimization adjusting lodging tier and paid activities count"""
        total = itinerary.get("total_estimated_cost", 0)
        optimized = dict(itinerary)
        score = 1.0
        if budget_total and total > budget_total:
            # Reduce cost by 10% as a placeholder optimization
            optimized["total_estimated_cost"] = round(total * 0.9, 2)
            score = max(0.0, 1 - (optimized["total_estimated_cost"] - budget_total) / max(budget_total, 1))
        elif budget_total:
            # Slightly increase quality within budget
            optimized["total_estimated_cost"] = min(total * 1.05, budget_total)
            score = 1.0
        return optimized, float(score)

    def _fetch_real_time_updates(self, destination: str) -> Dict[str, Any]:
        """Simulate real-time signals such as weather advisories or closures"""
        # Placeholder: in reality, call weather, events, transit APIs
        return {
            "advisory": f"Light showers expected in {destination}. Pack a light rain jacket."
        }

    def _book_itinerary_easemytrip(self, itinerary: Dict[str, Any], traveler_name: str) -> Dict[str, Any]:
        """Simulate booking with EaseMyTrip inventory and return reservation refs"""
        # Placeholder: This would call EaseMyTrip partner APIs for flights/hotels/activities
        # Here we just return mocked booking references
        return {
            "provider": "EaseMyTrip",
            "traveler": traveler_name,
            "reservations": [
                {"type": "hotel", "ref": "EMT-HOT-123456", "status": "reserved"},
                {"type": "flight", "ref": "EMT-FLT-654321", "status": "reserved"}
            ],
            "hold_expiry": (datetime.utcnow()).isoformat() + "Z"
        }

    def _process_payment(self, booking: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate payment processing and return a receipt"""
        amount = 0.0
        # If itinerary had a total, prefer that; else mock compute
        # In many real systems, the payment amount comes from pricing quotes at booking time
        try:
            amount = float(booking.get("amount", 0.0))
        except Exception:
            amount = 0.0
        if amount <= 0:
            amount = 999.0  # placeholder
        return {
            "status": "paid",
            "amount": amount,
            "currency": "USD",
            "transaction_id": "PAY-EMT-0001",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    def _generate_recommendations(self, memo_content: str) -> List[str]:
        """Extract actionable next steps from memo"""
        recommendations: List[str] = []
        for line in memo_content.split("\n"):
            lower = line.lower()
            if any(w in lower for w in ["recommend", "book", "confirm", "should", "next"]):
                recommendations.append(line.strip())
        return recommendations[:5]

    def plan_trip(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Main method to plan a personalized trip end-to-end"""
        traveler_name = preferences.get("traveler_name", "Traveler")
        initial_state = TripPlanningState(
            traveler_name=traveler_name,
            preferences=preferences,
            constraints={},
            destination_data={},
            itinerary={},
            recommendations=[],
            budget_fit_score=0.0,
            booking_details={},
            payment_receipt={},
            messages=[HumanMessage(content=f"Plan trip for: {traveler_name}")]
        )

        final_state = self.workflow.invoke(initial_state)

        return {
            "traveler_name": final_state["traveler_name"],
            "itinerary": final_state["itinerary"],
            "budget_fit_score": final_state.get("budget_fit_score", 0.0),
            "booking_details": final_state.get("booking_details", {}),
            "payment_receipt": final_state.get("payment_receipt", {}),
            "recommendations": final_state.get("recommendations", []),
            "workflow_messages": final_state["messages"]
        }


# Example usage
if __name__ == "__main__":
    agent = TravelOrchestrationAgent()

    sample_preferences = {
        "traveler_name": "Alex Smith",
        "origin": "JFK",
        "destination": "Tokyo",
        "start_date": "2025-10-10",
        "end_date": "2025-10-17",
        "budget_total": 2500.0,
        "interests": ["culture", "food", "nightlife"],
        "travelers_count": 2,
        "accommodation_tier": "mid",
        "pace": "balanced"
    }

    result = agent.plan_trip(sample_preferences)

    print("=== PERSONALIZED TRIP PLAN ===")
    print(f"Traveler: {result['traveler_name']}")
    print(f"Budget Fit: {result['budget_fit_score']:.2f}")
    print(f"\nItinerary Memo:\n{result['itinerary'].get('memo', '')}")
    print(f"\nBooking: {json.dumps(result['booking_details'], indent=2)}")
    print(f"\nPayment: {json.dumps(result['payment_receipt'], indent=2)}")
    print(f"\nRecommendations: {result['recommendations']}")


