# Imports for the main root agent
from google.adk.agents.llm_agent import Agent
from itinery_generation_app.prompt import ROOT_AGENT_INSTR
from itinery_generation_app.sub_agents.itinery.agent import itinery_agent
from itinery_generation_app.sub_agents.clarifying_agent.agent import clarifing_agent
from itinery_generation_app.tools.memory import _load_precreated_itinerary

# Define the root agent that orchestrates the overall flow.
root_agent = Agent(
    model='gemini-2.5-flash',
    name="root_agent",
    description="The main travel concierge that handles the full workflow.",
    instruction=ROOT_AGENT_INSTR,
    sub_agents=[
        clarifing_agent, # Step 1: Clarify details with the user
        itinery_agent,            # Step 2: Plan the itinerary
    ],
    before_agent_callback=_load_precreated_itinerary,
)