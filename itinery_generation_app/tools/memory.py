"""The 'memorize' tool for several agents to affect session states."""

from datetime import datetime
from typing import Dict, Any

from google.adk.agents.callback_context import CallbackContext
from google.adk.sessions.state import State
from google.adk.tools import ToolContext

from itinery_generation_app.shared_libraries import constants

# Directly embed the JSON data here as a Python dictionary.
# This approach eliminates the need to read from a file, solving the
# "No such file or directory" error during deployment.
DEFAULT_ITINERARY_STATE = {
    "state": {
        "user_profile": {
            "passport_nationality": "US Citizen",
            "seat_preference": "window",
            "food_preference": "vegan",
            "allergies": [],
            "likes": [],
            "dislikes": [],
            "price_sensitivity": [],
            "home": {
                "event_type": "home",
                "address": "6420 Sequence Dr #400, San Diego, CA 92121, United States",
                "local_prefer_mode": "drive"
            }
        },
        "itinerary": {},
        "origin": "",
        "destination": "",
        "start_date": "",
        "end_date": "",
        "outbound_flight_selection": "",
        "outbound_seat_number": "",
        "return_flight_selection": "",
        "return_seat_number": "",
        "hotel_selection": "",
        "room_selection": "",
        "poi": "",
        "itinerary_datetime": "",
        "itinerary_start_date": "",
        "itinerary_end_date": ""
    }
}


def memorize_list(key: str, value: str, tool_context: ToolContext):
    """
    Memorize pieces of information.

    Args:
        key: the label indexing the memory to store the value.
        value: the information to be stored.
        tool_context: The ADK tool context.

    Returns:
        A status message.
    """
    mem_dict = tool_context.state
    if key not in mem_dict:
        mem_dict[key] = []
    if value not in mem_dict[key]:
        mem_dict[key].append(value)
    return {"status": f'Stored "{key}": "{value}"'}


def memorize(key: str, value: str, tool_context: ToolContext):
    """
    Memorize pieces of information, one key-value pair at a time.

    Args:
        key: the label indexing the memory to store the value.
        value: the information to be stored.
        tool_context: The ADK tool context.

    Returns:
        A status message.
    """
    mem_dict = tool_context.state
    mem_dict[key] = value
    return {"status": f'Stored "{key}": "{value}"'}


def forget(key: str, value: str, tool_context: ToolContext):
    """
    Forget pieces of information.

    Args:
        key: the label indexing the memory to store the value.
        value: the information to be removed.
        tool_context: The ADK tool context.

    Returns:
        A status message.
    """
    if tool_context.state[key] is None:
        tool_context.state[key] = []
    if value in tool_context.state[key]:
        tool_context.state[key].remove(value)
    return {"status": f'Removed "{key}": "{value}"'}


def _set_initial_states(source: Dict[str, Any], target: State | dict[str, Any]):
    """
    Setting the initial session state given a JSON object of states.

    Args:
        source: A JSON object of states.
        target: The session state object to insert into.
    """
    if constants.SYSTEM_TIME not in target:
        target[constants.SYSTEM_TIME] = str(datetime.now())

    if constants.ITIN_INITIALIZED not in target:
        target[constants.ITIN_INITIALIZED] = True

        target.update(source)

        itinerary = source.get(constants.ITIN_KEY, {})
        if itinerary:
            target[constants.ITIN_START_DATE] = itinerary[constants.START_DATE]
            target[constants.ITIN_END_DATE] = itinerary[constants.END_DATE]
            target[constants.ITIN_DATETIME] = itinerary[constants.START_DATE]


def _load_precreated_itinerary(callback_context: CallbackContext):
    """
    Sets up the initial state directly from an embedded dictionary.
    
    Args:
        callback_context: The callback context.
    """
    print(f"\nLoading Initial State from embedded JSON...\n")
    _set_initial_states(DEFAULT_ITINERARY_STATE["state"], callback_context.state)