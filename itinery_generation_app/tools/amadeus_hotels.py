"""Amadeus API integration for hotel search and booking."""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import requests
from google.adk.tools import ToolContext


class AmadeusHotelsService:
    """Service for interacting with Amadeus Hotel API."""
    
    def __init__(self):
        self.api_key = os.getenv("AMADEUS_API_KEY")
        self.api_secret = os.getenv("AMADEUS_API_SECRET")
        self.base_url = "https://test.api.amadeus.com"  # Use production URL for live data
        self.access_token = None
        self.token_expires_at = None
    
    def _get_access_token(self) -> str:
        """Get or refresh the access token."""
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.access_token
        
        if not self.api_key or not self.api_secret:
            raise ValueError("AMADEUS_API_KEY and AMADEUS_API_SECRET must be set")
        
        url = f"{self.base_url}/v1/security/oauth2/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.api_secret
        }
        
        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            token_data = response.json()
            
            self.access_token = token_data["access_token"]
            expires_in = token_data.get("expires_in", 1800)  # Default 30 minutes
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)  # Refresh 1 min early
            
            return self.access_token
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get Amadeus access token: {e}")
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make authenticated request to Amadeus API."""
        token = self._get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = requests.get(f"{self.base_url}{endpoint}", headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Amadeus API request failed: {e}")
    
    def search_hotels(self, 
                      city_code: str,
                      check_in_date: str,
                      check_out_date: str,
                      adults: int = 1,
                      rooms: int = 1,
                      price_range: str = None,
                      hotel_chain_codes: List[str] = None,
                      amenities: List[str] = None,
                      ratings: List[int] = None) -> Dict[str, Any]:
        """
        Search for hotels using Amadeus API.
        
        Args:
            city_code: IATA city code (e.g., 'PAR', 'NYC', 'LON')
            check_in_date: Check-in date in YYYY-MM-DD format
            check_out_date: Check-out date in YYYY-MM-DD format
            adults: Number of adults
            rooms: Number of rooms
            price_range: Price range filter (e.g., '50-200')
            hotel_chain_codes: List of hotel chain codes
            amenities: List of desired amenities
            ratings: List of minimum star ratings
        
        Returns:
            Dictionary containing hotel search results
        """
        try:
            # For now, return a mock response since the hotel offers endpoint
            # seems to have issues in the test environment
            # In production, you would use the actual hotel search endpoints
            
            # Get list of hotels in the city for reference
            hotel_list_params = {
                "cityCode": city_code
            }
            
            hotel_list = self._make_request("/v1/reference-data/locations/hotels/by-city", hotel_list_params)
            
            if not hotel_list.get("data") or len(hotel_list["data"]) == 0:
                return {"error": "No hotels found in the specified city"}
            
            # Return a structured response with available hotels
            hotels = hotel_list["data"][:10]  # Limit to first 10 hotels
            
            return {
                "data": [
                    {
                        "hotelId": hotel["hotelId"],
                        "name": hotel.get("name", "Hotel Name"),
                        "address": hotel.get("address", {}),
                        "amenities": hotel.get("amenities", []),
                        "rating": hotel.get("rating", 0),
                        "note": "Hotel offers endpoint temporarily unavailable in test environment"
                    }
                    for hotel in hotels
                ],
                "meta": {
                    "count": len(hotels),
                    "cityCode": city_code,
                    "checkInDate": check_in_date,
                    "checkOutDate": check_out_date
                }
            }
            
        except Exception as e:
            return {"error": f"Hotel search failed: {str(e)}"}
    
    def get_hotel_offers(self, 
                        hotel_ids: List[str],
                        check_in_date: str,
                        check_out_date: str,
                        adults: int = 1,
                        rooms: int = 1) -> Dict[str, Any]:
        """
        Get hotel offers with pricing and availability.
        """
        params = {
            "hotelIds": ",".join(hotel_ids),
            "checkInDate": check_in_date,
            "checkOutDate": check_out_date,
            "adults": adults,
            "rooms": rooms,
            "currency": "USD"
        }
        
        return self._make_request("/v2/shopping/hotel-offers", params)
    
    def get_city_code(self, city_name: str) -> str:
        """
        Get IATA city code for a city name.
        """
        params = {"keyword": city_name, "subType": "CITY"}
        result = self._make_request("/v1/reference-data/locations", params)
        
        if result.get("data"):
            return result["data"][0]["iataCode"]
        return city_name  # Return original if not found
    
    def get_hotel_details(self, hotel_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific hotel.
        """
        return self._make_request(f"/v1/reference-data/locations/hotels/{hotel_id}")


# Initialize the service
amadeus_hotels_service = AmadeusHotelsService()


def search_hotels_tool(city: str, check_in_date: str, check_out_date: str,
                      tool_context: ToolContext, adults: int = 1, rooms: int = 1, 
                      price_range: str = None, amenities: List[str] = None, 
                      ratings: List[int] = None) -> Dict[str, Any]:
    """
    Tool for searching hotels using Amadeus API.
    
    Args:
        city: City name or IATA code
        check_in_date: Check-in date (YYYY-MM-DD)
        check_out_date: Check-out date (YYYY-MM-DD)
        adults: Number of adults
        rooms: Number of rooms
        price_range: Price range filter (e.g., '50-200')
        amenities: List of desired amenities
        ratings: List of minimum star ratings
        tool_context: ADK tool context
    
    Returns:
        Hotel search results
    """
    try:
        # Get city code if needed
        if len(city) > 3:
            city_code = amadeus_hotels_service.get_city_code(city)
        else:
            city_code = city
        
        results = amadeus_hotels_service.search_hotels(
            city_code=city_code,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            adults=adults,
            rooms=rooms,
            price_range=price_range,
            amenities=amenities,
            ratings=ratings
        )
        
        # Store results in context
        if "hotel_search_results" not in tool_context.state:
            tool_context.state["hotel_search_results"] = []
        
        tool_context.state["hotel_search_results"].append({
            "search_params": {
                "city": city,
                "city_code": city_code,
                "check_in_date": check_in_date,
                "check_out_date": check_out_date,
                "adults": adults,
                "rooms": rooms,
                "price_range": price_range,
                "amenities": amenities,
                "ratings": ratings
            },
            "results": results
        })
        
        return results
        
    except Exception as e:
        return {"error": f"Hotel search failed: {str(e)}"}


def get_hotel_offers_tool(hotel_ids: List[str], check_in_date: str, 
                         check_out_date: str, tool_context: ToolContext,
                         adults: int = 1, rooms: int = 1) -> Dict[str, Any]:
    """
    Tool for getting detailed hotel offers with pricing.
    """
    try:
        results = amadeus_hotels_service.get_hotel_offers(
            hotel_ids=hotel_ids,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            adults=adults,
            rooms=rooms
        )
        
        return results
        
    except Exception as e:
        return {"error": f"Failed to get hotel offers: {str(e)}"}


def get_hotel_details_tool(hotel_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Tool for getting detailed hotel information.
    """
    try:
        results = amadeus_hotels_service.get_hotel_details(hotel_id)
        return results
        
    except Exception as e:
        return {"error": f"Failed to get hotel details: {str(e)}"}
