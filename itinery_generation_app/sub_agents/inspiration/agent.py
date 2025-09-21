"""Inspiration agent. A pre-booking agent covering the ideation part of the trip."""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from itinery_generation_app.shared_libraries.types import DestinationIdeas, POISuggestions, json_response_config
from itinery_generation_app.sub_agents.inspiration import prompt
from itinery_generation_app.tools.places import map_tool


place_agent = Agent(
    model="gemini-2.5-flash",
    name="place_agent",
    instruction=prompt.PLACE_AGENT_INSTR,
    description="This agent suggests a few destination given some user preferences",
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    output_schema=DestinationIdeas,
    output_key="place",
    generate_content_config=json_response_config,
)

poi_agent = Agent(
    model="gemini-2.5-flash",
    name="poi_agent",
    description="This agent suggests a few activities and points of interests given a destination",
    instruction=prompt.POI_AGENT_INSTR,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    output_schema=POISuggestions,
    output_key="poi",
    generate_content_config=json_response_config,
)

inspiration_agent = Agent(
    model="gemini-2.5-flash",
    name="inspiration_agent",
    description="A travel inspiration agent who inspire users, and discover their next vacations; Provide information about places, activities, interests,",
    instruction=prompt.INSPIRATION_AGENT_INSTR,
    tools=[AgentTool(agent=place_agent), AgentTool(agent=poi_agent), map_tool],
)
