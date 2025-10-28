"""Amadeus API integration for flight search and booking.

This module provides the service class and agent-callable tool functions
for interacting with the Amadeus Flight Search APIs.
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import requests
from google.adk.tools import ToolContext

# --- Service Class for Amadeus API Interaction ---

class AmadeusFlightsService:
    """
    Service class to handle all interactions with the Amadeus Flight APIs.
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
            # Include response text for better debugging if available
            error_details = e.response.text if e.response else "No response from server"
            raise Exception(f"Amadeus API request to {endpoint} failed: {e}. Details: {error_details}")

    def search_flights(self,
                      origin: str,
                      destination: str,
                      departure_date: str,
                      return_date: Optional[str] = None,
                      adults: int = 1,
                      children: int = 0,
                      infants: int = 0,
                      travel_class: str = "ECONOMY",
                      max_price: Optional[int] = None) -> Dict[str, Any]:
        """
        Searches for flight offers based on a comprehensive set of criteria.
        """
        params = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": departure_date,
            "adults": adults,
            "children": children,
            "infants": infants,
            "travelClass": travel_class.upper(),
            "currencyCode": "USD",
            "max": 10  # Limit results to a manageable number
        }

        if return_date:
            params["returnDate"] = return_date

        if max_price:
            params["maxPrice"] = max_price

        return self._make_request("/v2/shopping/flight-offers", params)

    def get_airport_city_code(self, query: str) -> str:
        """
        Gets the IATA code for a city or airport name to ensure compatibility with API calls.
        """
        params = {"keyword": query, "subType": "AIRPORT,CITY"}
        result = self._make_request("/v1/reference-data/locations", params)

        if result and result.get("data"):
            return result["data"][0]["iataCode"]
        return query  # Return original query if no code is found


# --- Agent-Callable Tools ---

# Initialize the service as a singleton to be used by the tool functions
amadeus_flights_service = AmadeusFlightsService()


def search_flights_tool(
    origin: str,
    destination: str,
    departure_date: str,
    tool_context: ToolContext,
    return_date: Optional[str] = None,
    adults: int = 1,
    travel_class: str = "ECONOMY",
    max_price: Optional[int] = None
) -> Dict[str, Any]:
    """
    Searches for one-way or round-trip flight offers. Use this to find available
    flights with pricing based on origin, destination, dates, and other preferences.

    Args:
        origin: The starting city name or IATA airport code (e.g., "New York", "JFK").
        destination: The destination city name or IATA airport code (e.g., "London", "LHR").
        departure_date: The departure date in YYYY-MM-DD format.
        return_date: The return date in YYYY-MM-DD format. Omit for one-way flights.
        adults: The number of adult passengers (age 12+). Defaults to 1.
        travel_class: The desired cabin class. Can be ECONOMY, PREMIUM_ECONOMY, BUSINESS, or FIRST. Defaults to ECONOMY.
        max_price: The maximum total price for the flight in USD. Optional.
        tool_context: The execution context for the tool provided by the ADK.

    Returns:
        A dictionary containing flight offer data from the Amadeus API, or an
        error dictionary if the search fails.
    """
    try:
        # Convert city names to IATA codes for reliability if they aren't already codes
        origin_code = amadeus_flights_service.get_airport_city_code(origin) if len(origin) > 3 else origin
        destination_code = amadeus_flights_service.get_airport_city_code(destination) if len(destination) > 3 else destination

        results = amadeus_flights_service.search_flights(
            origin=origin_code,
            destination=destination_code,
            departure_date=departure_date,
            return_date=return_date,
            adults=adults,
            travel_class=travel_class,
            max_price=max_price
        )
        return results

    except Exception as e:
        # Return a structured error message for the agent to process
        return {
            "error": True,
            "message": f"An error occurred during the flight search: {str(e)}",
            "search_params": {
                "origin": origin,
                "destination": destination,
                "departure_date": departure_date,
                "return_date": return_date
            }
        }


def get_flight_offers_tool(
    origin: str,
    destination: str,
    departure_date: str,
    tool_context: ToolContext,
    return_date: Optional[str] = None,
    adults: int = 1
) -> Dict[str, Any]:
    """
    A simplified tool to get flight offers with pricing and booking details.
    Prefer 'search_flights_tool' for more detailed searches with more options.

    Args:
        origin: The starting IATA airport code (e.g., "JFK").
        destination: The destination IATA airport code (e.g., "LHR").
        departure_date: The departure date in YYYY-MM-DD format.
        return_date: The return date in YYYY-MM-DD format. Omit for one-way flights.
        adults: The number of adult passengers.
        tool_context: The execution context for the tool provided by the ADK.

    Returns:
        A dictionary containing flight offer data from the Amadeus API, or an
        error dictionary if the request fails.
    """
    try:
        # This tool uses the same underlying service method as search_flights_tool but with fewer params
        results = amadeus_flights_service.search_flights(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            adults=adults
        )
        return results

    except Exception as e:
        # Return a structured error message
        return {
            "error": True,
            "message": f"Failed to get flight offers: {str(e)}"
        }