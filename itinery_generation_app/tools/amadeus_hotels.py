"""Amadeus API integration for hotel search and booking.

This module provides the service class and agent-callable tool functions
for interacting with the Amadeus Hotel Search APIs.
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import requests
from google.adk.tools import ToolContext

# --- Service Class for Amadeus API Interaction ---

class AmadeusHotelsService:
    """
    Service class to handle all interactions with the Amadeus Hotel APIs.
    Manages API credentials, authentication (OAuth2), and request execution.
    """

    def __init__(self):
        """Initializes the Amadeus service, loading credentials from environment variables."""
        self.api_key = os.getenv("AMADEUS_CLIENT_ID")
        self.api_secret = os.getenv("AMADEUS_CLIENT_SECRET")
        self.base_url = "https://test.api.amadeus.com"  # Use production URL for live data
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None

        if not self.api_key or not self.api_secret:
            raise ValueError("AMADEUS_API_KEY and AMADEUS_API_SECRET environment variables must be set.")

    def _get_access_token(self) -> str:
        """
        Retrieves a new OAuth2 access token from Amadeus if the current one is
        missing or expired. Caches the token for reuse.
        """
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.access_token

        url = f"{self.base_url}/v1/security/oauth2/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.api_secret
        }

        try:
            response = requests.post(url, headers=headers, data=data, timeout=10)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            token_data = response.json()

            self.access_token = token_data["access_token"]
            # Refresh token 60 seconds before it actually expires as a safety buffer
            expires_in = token_data.get("expires_in", 1799)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)

            return self.access_token
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get Amadeus access token: {e}")

    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Makes an authenticated GET request to a specified Amadeus API endpoint.
        """
        token = self._get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        full_url = f"{self.base_url}{endpoint}"

        try:
            response = requests.get(full_url, headers=headers, params=params, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_details = e.response.text if e.response else "No response from server"
            raise Exception(f"Amadeus API request to {endpoint} failed: {e}. Details: {error_details}")

    def search_hotels(self, city_code: str, **kwargs) -> Dict[str, Any]:
        """
        Searches for available hotels in a given city.

        NOTE: The Amadeus test environment's Hotel Search v3 endpoint can be unreliable.
        This function provides a stable workaround by fetching a list of hotels in the city
        from a different endpoint, which is more reliable for demonstration purposes.
        """
        try:
            hotel_list_params = {"cityCode": city_code}
            hotel_list_response = self._make_request("/v1/reference-data/locations/hotels/by-city", hotel_list_params)

            if not hotel_list_response.get("data"):
                return {"data": [], "message": "No hotels found in the specified city."}

            # Return a structured response simulating a search result
            hotels_found = hotel_list_response["data"][:10]  # Limit to 10 for brevity
            return {
                "data": hotels_found,
                "meta": {
                    "count": len(hotels_found),
                    "search_parameters": {"cityCode": city_code, **kwargs},
                    "note": "This is a simulated search result from the hotel list endpoint due to test environment limitations."
                }
            }
        except Exception as e:
            raise Exception(f"Hotel search failed: {str(e)}")

    def get_city_code(self, city_name: str) -> str:
        """Gets the IATA code for a city name."""
        params = {"keyword": city_name, "subType": "CITY"}
        result = self._make_request("/v1/reference-data/locations", params)

        if result and result.get("data"):
            return result["data"][0]["iataCode"]
        return city_name # Return original if not found

    def get_hotel_details(self, hotel_id: str) -> Dict[str, Any]:
        """Gets detailed information about a specific hotel by its ID."""
        return self._make_request(f"/v3/shopping/hotel-offers/{hotel_id}")


# --- Agent-Callable Tools ---

# Initialize the service as a singleton to be used by the tool functions
amadeus_hotels_service = AmadeusHotelsService()


def search_hotels_tool(
    city: str,
    check_in_date: str,
    check_out_date: str,
    tool_context: ToolContext,
    adults: int = 1,
    rooms: int = 1
) -> Dict[str, Any]:
    """
    Searches for available hotels in a specific city for given dates.

    Args:
        city: The name of the city (e.g., "Paris", "New York").
        check_in_date: The check-in date in YYYY-MM-DD format.
        check_out_date: The check-out date in YYYY-MM-DD format.
        adults: Number of adults per room. Defaults to 1.
        rooms: Number of rooms to book. Defaults to 1.
        tool_context: The execution context for the tool provided by the ADK.

    Returns:
        A dictionary containing a list of available hotels or an error message.
    """
    try:
        # Convert city name to IATA code for reliability
        city_code = amadeus_hotels_service.get_city_code(city) if len(city) > 3 else city

        results = amadeus_hotels_service.search_hotels(
            city_code=city_code,
            checkInDate=check_in_date,
            checkOutDate=check_out_date,
            adults=adults,
            roomQuantity=rooms
        )
        
        # Store results in context
        if "hotel_search_results" not in tool_context.state:
            tool_context.state["hotel_search_results"] = []
        
        tool_context.state["hotel_search_results"].append({
            "search_params": {
                "city": city,
                "check_in_date": check_in_date,
                "check_out_date": check_out_date,
                "adults": adults,
                "rooms": rooms
            },
            "results": results
        })

        return results

    except Exception as e:
        return {"error": f"Hotel search failed: {str(e)}"}


# def get_hotel_offers_tool(hotel_ids: List[str], check_in_date: str, 
#                           check_out_date: str, tool_context: ToolContext,
#                           adults: int = 1, rooms: int = 1) -> Dict[str, Any]:
#     """
#     Tool for getting detailed hotel offers with pricing.
    
#     Args:
#         hotel_ids: A list of unique hotel IDs.
#         check_in_date: The check-in date in YYYY-MM-DD format.
#         check_out_date: The check-out date in YYYY-MM-DD format.
#         adults: Number of adults per room. Defaults to 1.
#         rooms: Number of rooms to book. Defaults to 1.
#         tool_context: The execution context for the tool provided by the ADK.

#     Returns:
#         A dictionary containing detailed hotel offer data or an error message.
#     """
#     try:
#         results = amadeus_hotels_service.get_hotel_offers(
#             hotel_ids=hotel_ids,
#             check_in_date=check_in_date,
#             check_out_date=check_out_date,
#             adults=adults,
#             rooms=rooms
#         )

#         if "hotel_offers_results" not in tool_context.state:
#             tool_context.state["hotel_offers_results"] = []
        
#         tool_context.state["hotel_offers_results"].append({
#             "search_params": {"hotel_ids": hotel_ids},
#             "results": results
#         })
        
#         return results
        
#     except Exception as e:
#         return {"error": f"Failed to get hotel offers: {str(e)}"}


def get_hotel_details_tool(hotel_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Retrieves detailed information, including price and room types, for a specific hotel.
    Use this function after finding a hotel with 'search_hotels_tool' to get booking details.

    Args:
        hotel_id: The unique ID of the hotel, obtained from a previous hotel search.
        tool_context: The execution context for the tool provided by the ADK.

    Returns:
        A dictionary with detailed hotel offer information or an error message.
    """
    try:
        results = amadeus_hotels_service.get_hotel_details(hotel_id)

        # Store results in context
        if "hotel_details_results" not in tool_context.state:
            tool_context.state["hotel_details_results"] = []
        
        tool_context.state["hotel_details_results"].append({
            "search_params": {"hotel_id": hotel_id},
            "results": results
        })
        
        return results

    except Exception as e:
        return {
            "error": True,
            "message": f"Failed to get details for hotel ID {hotel_id}: {str(e)}"
        }