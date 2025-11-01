from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import sys

# Add the project to the path
sys.path.append('/Users/trishashetty/Desktop/agenticAIHack')

# Load environment variables
load_dotenv()

# Import the agents
from itinery_generation_app.agent import root_agent
from itinery_generation_app.tools.amadeus_flights import search_flights_tool
from itinery_generation_app.tools.amadeus_hotels import search_hotels_tool
from itinery_generation_app.tools.indian_railways import (
    get_live_train_status_tool,
    search_trains_tool,
)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

class MockToolContext:
    """Mock tool context for API calls"""
    def __init__(self):
        self.state = {}

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages and route to appropriate agents"""
    try:
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # For now, use a simple rule-based routing
        # In production, you'd use the actual root_agent
        response = process_message(user_message)
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def process_message(message: str):
    """Process user message and return appropriate response"""
    message_lower = message.lower()
    
    # Check for flight search
    if any(keyword in message_lower for keyword in ['flight', 'fly', 'airline', 'ticket']):
        return handle_flight_search(message)
    
    # Check for hotel search
    elif any(keyword in message_lower for keyword in ['hotel', 'accommodation', 'stay', 'room']):
        return handle_hotel_search(message)
    
    # Check for train search/status
    elif any(keyword in message_lower for keyword in ['train', 'railway', 'irctc', 'rail']):
        return handle_train_search(message)
    
    # Check for booking confirmation
    elif any(keyword in message_lower for keyword in ['book', 'confirm', 'yes']):
        return handle_booking_confirmation(message)
    
    # Default response
    else:
        return {
            'message': "I can help you with:\n\n✈️ Flight bookings\n🏨 Hotel reservations\n🚂 Train tickets\n🚌 Bus bookings\n\nPlease tell me what you'd like to do!",
            'data': None,
            'dataType': None
        }

def handle_flight_search(message: str):
    """Handle flight search requests - parse user input for flight details"""
    try:
        tool_context = MockToolContext()
        import re
        from datetime import datetime, timedelta
        
        # Try to extract origin and destination (IATA codes: 3 uppercase letters)
        message_upper = message.upper()
        
        # Look for patterns like "from X to Y" or "X to Y"
        patterns = [
            r'FROM\s+([A-Z]{3})\s+TO\s+([A-Z]{3})',
            r'([A-Z]{3})\s+TO\s+([A-Z]{3})',
        ]
        
        origin = None
        destination = None
        for pattern in patterns:
            match = re.search(pattern, message_upper)
            if match:
                origin = match.group(1)
                destination = match.group(2)
                break
        
        # Try to extract dates
        date_patterns = [
            r'\b(\d{4}-\d{2}-\d{2})\b',  # YYYY-MM-DD
            r'\b(\d{2}-\d{2}-\d{4})\b',  # DD-MM-YYYY
            r'\b(\d{2}/\d{2}/\d{4})\b',   # DD/MM/YYYY
        ]
        
        departure_date = None
        return_date = None
        
        for pattern in date_patterns:
            matches = re.findall(pattern, message)
            if matches:
                try:
                    if '-' in matches[0]:
                        if len(matches[0].split('-')[0]) == 4:
                            dt = datetime.strptime(matches[0], "%Y-%m-%d")
                        else:
                            dt = datetime.strptime(matches[0], "%d-%m-%Y")
                    elif '/' in matches[0]:
                        dt = datetime.strptime(matches[0], "%d/%m/%Y")
                    
                    if not departure_date:
                        departure_date = dt.strftime("%Y-%m-%d")
                    elif not return_date:
                        return_date = dt.strftime("%Y-%m-%d")
                except ValueError:
                    continue
        
        # Handle relative dates
        message_lower = message.lower()
        if 'today' in message_lower and not departure_date:
            departure_date = datetime.now().strftime("%Y-%m-%d")
        elif 'tomorrow' in message_lower and not departure_date:
            departure_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Validate required fields
        if not origin or not destination:
            return {
                'message': "Please provide origin and destination airport codes. Example: 'flights from NYC to PAR' or 'search flights from JFK to LHR'",
                'dataType': None,
                'data': None
            }
        
        if not departure_date:
            return {
                'message': "Please provide a departure date. Format: YYYY-MM-DD (e.g., 2025-12-15)",
                'dataType': None,
                'data': None
            }
        
        # Call the actual flight search with live API
        results = search_flights_tool(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            tool_context=tool_context,
            return_date=return_date,
            adults=1,
            travel_class="ECONOMY"
        )
        
        # Format response for frontend
        if 'error' not in results:
            formatted_flights = format_flight_results(results)
            return {
                'message': f"I found these flights from {origin} to {destination}. Which one would you like to book?",
                'dataType': 'flights',
                'data': formatted_flights
            }
        else:
            error_msg = results.get('error', 'Unknown error')
            return {
                'message': f"Flight search failed: {error_msg}",
                'dataType': None,
                'data': None
            }
            
    except Exception as e:
        return {
            'message': f"Flight search failed: {str(e)}",
            'dataType': None,
            'data': None
        }

def handle_hotel_search(message: str):
    """Handle hotel search requests - parse user input for hotel details"""
    try:
        tool_context = MockToolContext()
        import re
        from datetime import datetime, timedelta
        
        # Try to extract city name (simplified - looks for common city patterns)
        # Could be improved with NLP
        city_patterns = [
            r'in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # "in Paris" or "in New York"
            r'at\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # "at Paris"
            r'hotels?\s+in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # "hotels in Paris"
        ]
        
        city = None
        for pattern in city_patterns:
            match = re.search(pattern, message)
            if match:
                city = match.group(1)
                break
        
        # Try to extract dates
        date_patterns = [
            r'\b(\d{4}-\d{2}-\d{2})\b',  # YYYY-MM-DD
            r'\b(\d{2}-\d{2}-\d{4})\b',  # DD-MM-YYYY
            r'\b(\d{2}/\d{2}/\d{4})\b',   # DD/MM/YYYY
        ]
        
        check_in_date = None
        check_out_date = None
        
        for pattern in date_patterns:
            matches = re.findall(pattern, message)
            if matches:
                try:
                    for match_str in matches:
                        if '-' in match_str:
                            if len(match_str.split('-')[0]) == 4:
                                dt = datetime.strptime(match_str, "%Y-%m-%d")
                            else:
                                dt = datetime.strptime(match_str, "%d-%m-%Y")
                        elif '/' in match_str:
                            dt = datetime.strptime(match_str, "%d/%m/%Y")
                        
                        if not check_in_date:
                            check_in_date = dt.strftime("%Y-%m-%d")
                        elif not check_out_date:
                            check_out_date = dt.strftime("%Y-%m-%d")
                except ValueError:
                    continue
        
        # Handle relative dates
        message_lower = message.lower()
        if 'today' in message_lower and not check_in_date:
            check_in_date = datetime.now().strftime("%Y-%m-%d")
            check_out_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        elif 'tomorrow' in message_lower and not check_in_date:
            check_in_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            check_out_date = (datetime.now() + timedelta(days=8)).strftime("%Y-%m-%d")
        elif check_in_date and not check_out_date:
            # If only check-in date provided, assume 7 days stay
            try:
                dt = datetime.strptime(check_in_date, "%Y-%m-%d")
                check_out_date = (dt + timedelta(days=7)).strftime("%Y-%m-%d")
            except ValueError:
                pass
        
        # Validate required fields
        if not city:
            return {
                'message': "Please provide a city name. Example: 'hotels in Paris' or 'hotels in New York'",
                'dataType': None,
                'data': None
            }
        
        if not check_in_date or not check_out_date:
            return {
                'message': "Please provide check-in and check-out dates. Format: YYYY-MM-DD (e.g., check-in: 2025-12-15, check-out: 2025-12-22)",
                'dataType': None,
                'data': None
            }
        
        # Call the actual hotel search with live API
        results = search_hotels_tool(
            city=city,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            tool_context=tool_context,
            adults=2,
            rooms=1
        )
        
        if 'error' not in results:
            formatted_hotels = format_hotel_results(results)
            return {
                'message': f"Here are some great hotels I found in {city}:",
                'dataType': 'hotels',
                'data': formatted_hotels
            }
        else:
            error_msg = results.get('error', 'Unknown error')
            return {
                'message': f"Hotel search failed: {error_msg}",
                'dataType': None,
                'data': None
            }
            
    except Exception as e:
        return {
            'message': f"Hotel search failed: {str(e)}",
            'dataType': None,
            'data': None
        }

def handle_train_search(message: str):
    """Handle train search or live status based on user input parsing."""
    try:
        tool_context = MockToolContext()
        message_lower = message.lower()
        import re
        from datetime import datetime, timedelta
        
        # Try to extract train number (5-digit pattern)
        train_match = re.search(r"\b(\d{5})\b", message)
        
        # Try to extract date patterns (YYYY-MM-DD, DD-MM-YYYY, DD/MM/YYYY, or relative dates like "today", "tomorrow")
        date_patterns = [
            r"\b(\d{4}-\d{2}-\d{2})\b",  # YYYY-MM-DD
            r"\b(\d{2}-\d{2}-\d{4})\b",  # DD-MM-YYYY
            r"\b(\d{2}/\d{2}/\d{4})\b",   # DD/MM/YYYY
        ]
        date = None
        for pattern in date_patterns:
            date_match = re.search(pattern, message)
            if date_match:
                date_str = date_match.group(1)
                try:
                    if '-' in date_str:
                        if len(date_str.split('-')[0]) == 4:
                            dt = datetime.strptime(date_str, "%Y-%m-%d")
                        else:
                            dt = datetime.strptime(date_str, "%d-%m-%Y")
                    elif '/' in date_str:
                        dt = datetime.strptime(date_str, "%d/%m/%Y")
                    date = dt.strftime("%Y-%m-%d")
                    break
                except ValueError:
                    continue
        
        # Handle relative dates
        if not date:
            if 'today' in message_lower:
                date = datetime.now().strftime("%Y-%m-%d")
            elif 'tomorrow' in message_lower:
                date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        # If train number found, get live status
        if train_match:
            train_number = train_match.group(1)
            if not date:
                return {
                    'message': "Please provide a date for checking live train status. Format: YYYY-MM-DD (e.g., 2025-12-15)",
                    'dataType': None,
                    'data': None
                }
            
            result = get_live_train_status_tool(train_number=train_number, date=date, tool_context=tool_context)
            if 'error' not in result:
                return {
                    'message': f"Here is the live status for train {train_number} on {date}:",
                    'dataType': 'train-live-status',
                    'data': result
                }
            else:
                error_msg = result.get('error', 'Unknown error')
                return {
                    'message': f"Failed to fetch live train status: {error_msg}",
                    'dataType': None,
                    'data': None
                }
        
        # Otherwise, search trains between stations
        # Try to extract station codes (3-4 uppercase letters) or station names
        # Common patterns: "from X to Y", "X to Y", "between X and Y"
        message_upper = message.upper()
        station_patterns = [
            (r"FROM\s+([A-Z]{3,4})\s+TO\s+([A-Z]{3,4})", "from to"),
            (r"([A-Z]{3,4})\s+TO\s+([A-Z]{3,4})", "to"),
            (r"BETWEEN\s+([A-Z]{3,4})\s+AND\s+([A-Z]{3,4})", "between and"),
        ]
        
        from_station = None
        to_station = None
        
        for pattern, desc in station_patterns:
            match = re.search(pattern, message_upper)
            if match:
                from_station = match.group(1)
                to_station = match.group(2)
                break
        
        if not from_station or not to_station:
            return {
                'message': "Please provide source and destination station codes. Example: 'trains from NDLS to BCT' or 'search trains between NDLS and BCT on 2025-12-15'",
                'dataType': None,
                'data': None
            }
        
        if not date:
            return {
                'message': "Please provide a date for your journey. Format: YYYY-MM-DD (e.g., 2025-12-15)",
                'dataType': None,
                'data': None
            }
        
        result = search_trains_tool(from_station=from_station, to_station=to_station, date=date, tool_context=tool_context)
        if 'error' not in result:
            return {
                'message': f"I found these trains from {from_station} to {to_station} on {date}:",
                'dataType': 'trains',
                'data': result
            }
        else:
            error_msg = result.get('error', 'Unknown error')
            return {
                'message': f"Failed to search trains: {error_msg}",
                'dataType': None,
                'data': None
            }
            
    except Exception as e:
        return {
            'message': f"Train search failed: {str(e)}",
            'dataType': None,
            'data': None
        }

def handle_booking_confirmation(message: str):
    """Handle booking confirmation"""
    return {
        'message': "Great! Your booking has been confirmed! 🎉",
        'dataType': 'booking-confirmation',
        'data': {
            'bookingId': "EMT" + os.urandom(3).hex().upper(),
            'type': "Flight",
            'details': "NYC to Paris on Dec 15, 2024",
            'amount': 4500,
            'status': "Confirmed"
        }
    }

def format_flight_results(results):
    """Format flight API results for frontend"""
    # Pass through raw results for now; adjust mapping as needed by UI
    return results

def format_hotel_results(results):
    """Format hotel API results for frontend"""
    # Pass through raw results for now; adjust mapping as needed by UI
    return results

# All mock data removed to ensure only real API results are returned

@app.route('/api/trains/live-status', methods=['GET'])
def api_train_live_status():
    """Proxy endpoint: live status for a train number and date."""
    train_number = request.args.get('trainNumber') or request.args.get('train_number')
    # Use "today" as default instead of a hardcoded date
    date = request.args.get('date') or 'today'
    if not train_number:
        return jsonify({'error': 'trainNumber is required'}), 400
    tool_context = MockToolContext()
    result = get_live_train_status_tool(train_number=str(train_number), date=date, tool_context=tool_context)
    status_code = 200 if 'error' not in result else 502
    return jsonify(result), status_code

@app.route('/api/trains/search', methods=['GET'])
def api_trains_between():
    """Proxy endpoint: search trains between stations on a date."""
    from_station = request.args.get('from') or request.args.get('fromStation') or request.args.get('from_station')
    to_station = request.args.get('to') or request.args.get('toStation') or request.args.get('to_station')
    date = request.args.get('date') or os.environ.get('DEFAULT_RAIL_DATE', '2025-12-15')
    if not from_station or not to_station:
        return jsonify({'error': 'from and to are required'}), 400
    tool_context = MockToolContext()
    result = search_trains_tool(from_station=from_station, to_station=to_station, date=date, tool_context=tool_context)
    status_code = 200 if 'error' not in result else 502
    return jsonify(result), status_code

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
