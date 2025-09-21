from google.adk.agents.llm_agent import Agent
from google.adk.agents.parallel_agent import ParallelAgent
from itinery_generation_app.sub_agents.inspiration.agent import inspiration_agent
from itinery_generation_app.sub_agents.planning.agent import planning_agent
from itinery_generation_app.sub_agents.booking.agent import booking_agent
from itinery_generation_app.sub_agents.in_trip.agent import in_trip_agent
from itinery_generation_app.sub_agents.post_trip.agent import post_trip_agent
from itinery_generation_app.sub_agents.pre_trip.agent import pre_trip_agent
from itinery_generation_app.tools.memory import _load_precreated_itinerary

ROOT_AGENT_INSTR = """
You are a highly capable and friendly Travel Concierge. Your primary goal is to manage and orchestrate the entire travel lifecycle for a user, from initial inspiration to post-trip feedback.

Your responsibilities include:
1.  **Understanding the User's Needs**: Analyze the user's requests to determine the correct phase of their travel journey (e.g., just dreaming, actively planning, already on their trip).
2.  **Delegating to Sub-Agents**: Based on the user's intent, activate the appropriate sub-agent(s) to handle specific tasks. You must route the request to the correct specialized agent.
3.  **Synthesizing Information**: Receive information back from your sub-agents and present a coherent, helpful, and concise response to the user.
4.  **Maintaining Context**: Use the provided memory to recall previous interactions and itinerary details to provide a seamless experience.

Use your available tools to fulfill the user's request. Always be helpful, informative, and proactive in assisting with travel-related inquiries.
"""

# # The before_agent_callback is removed from the ParallelAgent
# parallel_itinerary_agent = ParallelAgent(
#     name="parallel_itinerary_agent",
#     description="Executes various travel-related tasks in parallel.",
#     agents=[
#         inspiration_agent,
#         planning_agent,
#         booking_agent,
#         pre_trip_agent,
#         in_trip_agent,
#         post_trip_agent,
#     ],
# )

itinery_agent = Agent(
    model='gemini-2.5-flash',
    name="root_agent",
    description="A Travel Concierge using the services of multiple sub-agents",
    instruction=ROOT_AGENT_INSTR,
    sub_agents=[
        inspiration_agent,
        planning_agent,
        booking_agent,
        pre_trip_agent,
        in_trip_agent,
        post_trip_agent,
    ],
    before_agent_callback=_load_precreated_itinerary,
)