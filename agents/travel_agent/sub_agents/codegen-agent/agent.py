import os
from google.adk.agents.llm_agent import Agent

GEMINI_MODEL = os.getenv("GEMINI_MODEL")

root_agent = Agent(
    model= GEMINI_MODE,
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
)
