"""Indian Railways integration for live train data via RapidAPI IRCTC."""

import os
from typing import Dict, Any
from datetime import datetime, timedelta
import requests
from google.adk.tools import ToolContext


class IndianRailwaysService:
    """Service for interacting with RapidAPI IRCTC API.
    
    Configured specifically for RapidAPI IRCTC (irctc1.p.rapidapi.com).
    """

    def __init__(self):
        # Default to RapidAPI IRCTC if not set
        self.base_url = os.getenv("RAIL_API_BASE_URL", "https://irctc1.p.rapidapi.com")
        self.api_key = os.getenv("RAIL_API_KEY", "")
        self.api_host = os.getenv("RAIL_API_HOST", "irctc1.p.rapidapi.com")

        if not self.api_key:
            raise ValueError("RAIL_API_KEY must be set to use Indian Railways integration")

    def _headers(self) -> Dict[str, str]:
        """Return headers for RapidAPI IRCTC authentication."""
        return {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": self.api_host
        }

    def _get(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make authenticated GET request to RapidAPI IRCTC."""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(url, headers=self._headers(), params=params or {}, timeout=20)
            
            # Check for subscription errors first
            if response.status_code == 403:
                try:
                    error_data = response.json()
                    if "not subscribed" in error_data.get("message", "").lower():
                        raise Exception(
                            "You are not subscribed to the IRCTC API on RapidAPI. "
                            "Please visit https://rapidapi.com/IRCTCAPI/api/irctc1 and subscribe to a plan."
                        )
                except (ValueError, KeyError):
                    pass
                
                raise Exception(
                    "403 Forbidden - Check your RapidAPI key. "
                    "Ensure RAIL_API_KEY is set correctly and you have an active subscription to IRCTC API. "
                    "Visit: https://rapidapi.com/IRCTCAPI/api/irctc1"
                )
            elif response.status_code == 429:
                raise Exception(
                    "429 Too Many Requests - Rate limit exceeded. "
                    "Please wait before making more requests."
                )
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            # Re-raise our custom exceptions
            if "not subscribed" in str(e).lower() or "403 Forbidden" in str(e) or "429 Too Many Requests" in str(e):
                raise
            raise Exception(f"Railways API request failed: {e}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Railways API request failed: {e}")

    def _date_to_start_day(self, date: str) -> int:
        """Convert date to startDay offset (1 = today, 2 = tomorrow, etc.).
        
        Args:
            date: Journey date in YYYY-MM-DD, YYYYMMDD, or relative ("today", "tomorrow")
        
        Returns:
            Integer day offset (1 for today, 2 for tomorrow, etc., max 30 days ahead)
        """
        try:
            today = datetime.now().date()
            
            # Handle relative dates
            date_lower = date.lower()
            if date_lower == "today":
                return 1
            elif date_lower == "tomorrow":
                return 2
            
            # Parse absolute dates
            if '-' in date:
                dt = datetime.strptime(date, "%Y-%m-%d").date()
            elif len(date) == 8 and date.isdigit():
                dt = datetime.strptime(date, "%Y%m%d").date()
            else:
                # Try DDMMYYYY format
                try:
                    dt = datetime.strptime(date, "%d%m%Y").date()
                except ValueError:
                    # Default to today if parsing fails
                    return 1
            
            # Calculate days difference
            delta = (dt - today).days + 1
            # Ensure it's between 1 (today) and 30 (reasonable limit for live status)
            return max(1, min(30, delta))
        except (ValueError, AttributeError):
            # Default to today if parsing fails
            return 1

    def get_live_train_status(self, train_number: str, date: str) -> Dict[str, Any]:
        """Fetch live train running status using RapidAPI IRCTC.

        Args:
            train_number: Numeric train number as string (e.g., "12952")
            date: Journey date in YYYY-MM-DD, YYYYMMDD format, or relative ("today", "tomorrow")
        """
        # RapidAPI IRCTC endpoint for live train status (actual endpoint from their docs)
        endpoint = os.getenv("RAIL_LIVE_STATUS_ENDPOINT", "/api/v1/liveTrainStatus")
        start_day = self._date_to_start_day(date)
        params = {
            "trainNo": train_number,
            "startDay": start_day
        }
        return self._get(endpoint, params)

    def _normalize_date(self, date: str) -> str:
        """Convert date to YYYY-MM-DD format expected by search API.
        
        Args:
            date: Journey date in various formats or relative ("today", "tomorrow")
        
        Returns:
            Date string in YYYY-MM-DD format
        """
        try:
            date_lower = date.lower()
            
            # Handle relative dates
            if date_lower == "today":
                return datetime.now().strftime("%Y-%m-%d")
            elif date_lower == "tomorrow":
                return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            
            # Parse absolute dates
            if '-' in date:
                # Already in YYYY-MM-DD or DD-MM-YYYY format
                if len(date.split('-')[0]) == 4:
                    # YYYY-MM-DD
                    dt = datetime.strptime(date, "%Y-%m-%d")
                else:
                    # DD-MM-YYYY
                    dt = datetime.strptime(date, "%d-%m-%Y")
                return dt.strftime("%Y-%m-%d")
            elif len(date) == 8 and date.isdigit():
                # YYYYMMDD format
                dt = datetime.strptime(date, "%Y%m%d")
                return dt.strftime("%Y-%m-%d")
            else:
                # Try DDMMYYYY format
                dt = datetime.strptime(date, "%d%m%Y")
                return dt.strftime("%Y-%m-%d")
        except (ValueError, AttributeError):
            # Default to today if parsing fails
            return datetime.now().strftime("%Y-%m-%d")

    def search_trains_between_stations(self, from_station: str, to_station: str, date: str) -> Dict[str, Any]:
        """Search trains between two stations using RapidAPI IRCTC.

        Args:
            from_station: Source station code (e.g., "NDLS" for New Delhi)
            to_station: Destination station code (e.g., "BCT" for Mumbai Central)
            date: Journey date in YYYY-MM-DD, YYYYMMDD format, or relative ("today", "tomorrow")
        """
        # RapidAPI IRCTC endpoint for train search (actual endpoint from their docs)
        endpoint = os.getenv("RAIL_SEARCH_ENDPOINT", "/api/v1/searchTrain")
        formatted_date = self._normalize_date(date)
        params = {
            "fromStationCode": from_station.upper(),
            "toStationCode": to_station.upper(),
            "dateOfJourney": formatted_date
        }
        return self._get(endpoint, params)


# Service instance - will be initialized when first used
_indian_railways_service = None


def _get_service() -> IndianRailwaysService:
    """Get or create the Indian Railways service instance."""
    global _indian_railways_service
    if _indian_railways_service is None:
        _indian_railways_service = IndianRailwaysService()
    return _indian_railways_service


def get_live_train_status_tool(train_number: str, date: str, tool_context: ToolContext) -> Dict[str, Any]:
    """Tool wrapper for live train status using RapidAPI IRCTC."""
    try:
        service = _get_service()
        result = service.get_live_train_status(train_number=train_number, date=date)
        tool_context.state.setdefault("train_live_status_results", []).append({
            "search_params": {"train_number": train_number, "date": date},
            "results": result,
        })
        return result
    except ValueError as e:
        # Missing API key or configuration
        return {"error": f"Configuration error: {str(e)}. Please set RAIL_API_KEY in environment variables."}
    except Exception as e:
        return {"error": f"Live train status failed: {str(e)}"}


def search_trains_tool(from_station: str, to_station: str, date: str, tool_context: ToolContext) -> Dict[str, Any]:
    """Tool wrapper for trains between stations using RapidAPI IRCTC."""
    try:
        service = _get_service()
        result = service.search_trains_between_stations(
            from_station=from_station, to_station=to_station, date=date
        )
        tool_context.state.setdefault("train_search_results", []).append({
            "search_params": {"from": from_station, "to": to_station, "date": date},
            "results": result,
        })
        return result
    except ValueError as e:
        # Missing API key or configuration
        return {"error": f"Configuration error: {str(e)}. Please set RAIL_API_KEY in environment variables."}
    except Exception as e:
        return {"error": f"Train search failed: {str(e)}"}


