import os
import sys
import json
from typing import Dict, Any
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from graph_workflow import TravelPlannerGraph

# Load environment variables
load_dotenv()

app = Flask(__name__)

class TravelPlannerService:
    """Service class for handling travel planning requests"""
    
    def __init__(self):
        google_api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY not found in environment variables")
        
        os.environ["GOOGLE_API_KEY"] = google_api_key
        
        self.graph = TravelPlannerGraph()
        # Store session states in memory (in production, use Redis or database)
        self.session_states = {}
    
    def process_request(self, user_input: str, session_id: str = None, previous_state: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a travel planning request with state persistence"""
        try:
            session_id = session_id or "default"
            
            # Get existing state or create new one
            if previous_state:
                # Use provided previous state
                initial_state = previous_state.copy()
                initial_state["user_input"] = user_input
                # Add new user input to conversation history
                initial_state["conversation_history"].append(f"User: {user_input}")
            elif session_id in self.session_states:
                # Use stored session state
                initial_state = self.session_states[session_id].copy()
                initial_state["user_input"] = user_input
                # Add new user input to conversation history
                initial_state["conversation_history"].append(f"User: {user_input}")
            else:
                # Create new state
                initial_state = {
                    "user_input": user_input,
                    "session_id": session_id,
                    "clarification_needed": False,
                    "clarification_questions": [],
                    "trip_preferences": {},
                    "itinerary_toc": {},
                    "success_criteria": [],
                    "data_quality_requirements": [],
                    "itinerary": {},
                    "final_response": "",
                    "conversation_history": [f"User: {user_input}"]
                }
            
            result = self.graph.workflow.invoke(initial_state)
            self.session_states[session_id] = result.copy()
            
            return result
            
        except Exception as e:
            return {
                "error": str(e),
                "status": "failed"
            }
    
    def get_session_state(self, session_id: str) -> Dict[str, Any]:
        """Get the current state for a session"""
        return self.session_states.get(session_id, {})

# Initialize service
travel_service = None

def initialize_service():
    global travel_service
    try:
        travel_service = TravelPlannerService()
        print("Travel service initialized successfully")
    except Exception as e:
        print(f"Failed to initialize travel service: {str(e)}")
        travel_service = None

@app.before_first_request
def before_first_request():
    initialize_service()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    if travel_service is None:
        return jsonify({"status": "unhealthy", "error": "Service not initialized"}), 503
    return jsonify({"status": "healthy"}), 200

@app.route('/plan-trip', methods=['POST'])
def plan_trip():
    """Main endpoint for trip planning"""
    if travel_service is None:
        return jsonify({"error": "Service not initialized"}), 503
        
    try:
        data = request.get_json()
        user_input = data.get('user_input', '')
        session_id = data.get('session_id', 'default')
        previous_state = data.get('previous_state', None)  # Allow passing previous state
        
        if not user_input:
            return jsonify({"error": "user_input is required"}), 400
        
        result = travel_service.process_request(user_input, session_id, previous_state)
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/continue-conversation', methods=['POST'])
def continue_conversation():
    """Endpoint for continuing conversation with clarifications"""
    if travel_service is None:
        return jsonify({"error": "Service not initialized"}), 503
        
    try:
        data = request.get_json()
        user_input = data.get('user_input', '')
        session_id = data.get('session_id', 'default')
        previous_state = data.get('previous_state', None)
        
        if not user_input:
            return jsonify({"error": "user_input is required"}), 400
        
        result = travel_service.process_request(user_input, session_id, previous_state)
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get-session', methods=['GET'])
def get_session():
    """Get current session state"""
    if travel_service is None:
        return jsonify({"error": "Service not initialized"}), 503
    
    try:
        session_id = request.args.get('session_id', 'default')
        state = travel_service.get_session_state(session_id)
        return jsonify(state), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def run_interactive():
    """Interactive CLI mode for testing"""
    print("🧭 AI-Powered Trip Planner")
    print("Type 'exit' to quit\n")
    
    # Initialize service for interactive mode
    if travel_service is None:
        initialize_service()
    
    if travel_service is None:
        print("Error: Could not initialize travel service")
        return
    
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ['exit', 'quit']:
            break
        
        if not user_input:
            continue
            
        try:
            result = travel_service.process_request(user_input)
            
            if result.get('clarification_needed'):
                print(f"\nBot: {result.get('final_response')}")
                for i, question in enumerate(result.get('clarification_questions', []), 1):
                    print(f"{i}. {question}")
                print()
                
                # Wait for clarification response
                clarification_input = input("Your response: ").strip()
                if clarification_input and clarification_input.lower() not in ['exit', 'quit']:
                    # Process clarification with previous state
                    follow_up_result = travel_service.process_request(clarification_input, "interactive", result)
                    print(f"\nBot: {follow_up_result.get('final_response')}\n")
            else:
                print(f"\nBot: {result.get('final_response')}\n")
                
        except Exception as e:
            print(f"Error: {str(e)}\n")

if __name__ == "__main__":
    # Check if running in development mode
    if os.getenv('FLASK_ENV') == 'development' or len(sys.argv) > 1 and sys.argv[1] == 'interactive':
        run_interactive()
    else:
        # Production mode - run Flask server
        port = int(os.environ.get('PORT', 8080))
        initialize_service()
        app.run(host='0.0.0.0', port=port)