"""Amadeus API integration for flight search and booking."""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import requests
from google.adk.tools import ToolContext


class AmadeusFlightsService:
    """Service for interacting with Amadeus Flight API."""
    
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
    
    def search_flights(self, 
                      origin: str, 
                      destination: str, 
                      departure_date: str,
                      return_date: str = None,
                      adults: int = 1,
                      children: int = 0,
                      infants: int = 0,
                      travel_class: str = "ECONOMY",
                      max_price: int = None,
                      currency_code: str = None) -> Dict[str, Any]:
        """
        Search for flights using Amadeus API.
        
        Args:
            origin: IATA code for origin airport (e.g., 'NYC', 'LAX')
            destination: IATA code for destination airport (e.g., 'PAR', 'LHR')
            departure_date: Departure date in YYYY-MM-DD format
            return_date: Return date in YYYY-MM-DD format (optional for one-way)
            adults: Number of adult passengers
            children: Number of child passengers
            infants: Number of infant passengers
            travel_class: Travel class (ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST)
            max_price: Maximum price filter (in the specified currency)
            currency_code: Currency code (e.g., 'INR', 'USD', 'EUR'). Defaults to INR, falls back to USD.
        
        Returns:
            Dictionary containing flight search results
        """
        # Default to INR if not specified, fallback to USD
        if not currency_code:
            currency_code = os.getenv("AMADEUS_CURRENCY", "INR")
        
        params = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": departure_date,
            "adults": adults,
            "children": children,
            "infants": infants,
            "travelClass": travel_class,
            "currencyCode": currency_code.upper(),
            "max": 10  # Limit results
        }
        
        if return_date:
            params["returnDate"] = return_date
        
        if max_price:
            params["maxPrice"] = max_price
        
        return self._make_request("/v2/shopping/flight-offers", params)
    
    def get_flight_offers(self, 
                         origin: str, 
                         destination: str, 
                         departure_date: str,
                         return_date: str = None,
                         adults: int = 1,
                         currency_code: str = None) -> Dict[str, Any]:
        """
        Get flight offers with pricing and booking details.
        
        Args:
            origin: IATA code for origin airport
            destination: IATA code for destination airport
            departure_date: Departure date in YYYY-MM-DD format
            return_date: Return date in YYYY-MM-DD format (optional)
            adults: Number of adult passengers
            currency_code: Currency code (e.g., 'INR', 'USD', 'EUR'). Defaults to INR, falls back to USD.
        """
        # Default to INR if not specified, fallback to USD
        if not currency_code:
            currency_code = os.getenv("AMADEUS_CURRENCY", "INR")
        
        params = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": departure_date,
            "adults": adults,
            "currencyCode": currency_code.upper()
        }
        
        if return_date:
            params["returnDate"] = return_date
        
        return self._make_request("/v2/shopping/flight-offers", params)
    
    def get_airport_city_code(self, city_name: str) -> str:
        """
        Get IATA code for a city name.
        """
        params = {"keyword": city_name, "subType": "AIRPORT"}
        result = self._make_request("/v1/reference-data/locations", params)
        
        if result.get("data"):
            return result["data"][0]["iataCode"]
        return city_name  # Return original if not found


# Initialize the service
amadeus_flights_service = AmadeusFlightsService()


def search_flights_tool(origin: str, destination: str, departure_date: str, 
                       tool_context: ToolContext, return_date: str = None, 
                       adults: int = 1, travel_class: str = "ECONOMY", 
                       max_price: int = None, currency_code: str = None) -> Dict[str, Any]:
    """
    Tool for searching flights using Amadeus API.
    
    Args:
        origin: Origin airport/city code
        destination: Destination airport/city code  
        departure_date: Departure date (YYYY-MM-DD)
        return_date: Return date (YYYY-MM-DD) - optional
        adults: Number of adult passengers
        travel_class: Travel class (ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST)
        max_price: Maximum price (in the specified currency)
        currency_code: Currency code (e.g., 'INR', 'USD', 'EUR'). Defaults to INR.
        tool_context: ADK tool context
    
    Returns:
        Flight search results
    """
    try:
        # Try to get city codes if not already IATA codes
        if len(origin) > 3:
            origin = amadeus_flights_service.get_airport_city_code(origin)
        if len(destination) > 3:
            destination = amadeus_flights_service.get_airport_city_code(destination)
        
        results = amadeus_flights_service.search_flights(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            adults=adults,
            travel_class=travel_class,
            max_price=max_price,
            currency_code=currency_code
        )
        
        # Store results in context
        if "flight_search_results" not in tool_context.state:
            tool_context.state["flight_search_results"] = []
        
        tool_context.state["flight_search_results"].append({
            "search_params": {
                "origin": origin,
                "destination": destination,
                "departure_date": departure_date,
                "return_date": return_date,
                "adults": adults,
                "travel_class": travel_class,
                "max_price": max_price
            },
            "results": results
        })
        
        return results
        
    except Exception as e:
        return {"error": f"Flight search failed: {str(e)}"}


def get_flight_offers_tool(origin: str, destination: str, departure_date: str,
                          tool_context: ToolContext, return_date: str = None, 
                          adults: int = 1, currency_code: str = None) -> Dict[str, Any]:
    """
    Tool for getting detailed flight offers with pricing.
    
    Args:
        origin: Origin airport/city code
        destination: Destination airport/city code
        departure_date: Departure date (YYYY-MM-DD)
        return_date: Return date (YYYY-MM-DD) - optional
        adults: Number of adult passengers
        currency_code: Currency code (e.g., 'INR', 'USD', 'EUR'). Defaults to INR.
        tool_context: ADK tool context
    
    Returns:
        Flight offers with pricing
    """
    try:
        results = amadeus_flights_service.get_flight_offers(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            adults=adults,
            currency_code=currency_code
        )
        
        return results
        
    except Exception as e:
        return {"error": f"Failed to get flight offers: {str(e)}"}
