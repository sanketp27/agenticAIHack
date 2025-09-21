# Imports for the clarifying agent and loop agent
from google.adk.agents.llm_agent import Agent
from google.adk.agents.loop_agent import LoopAgent
from itinery_generation_app.sub_agents.clarifying_agent.prompt import clarify_agent_prompt

# Define the single-use clarifying agent
clarifing_agent = Agent(
    model='gemini-2.5-flash',
    name='clarifing_agent',
    description='Gathers essential details for a travel itinerary.',
    instruction=clarify_agent_prompt,
)
