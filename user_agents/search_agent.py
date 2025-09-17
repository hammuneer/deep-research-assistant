"""
Search agent module.

Defines the SearchAgent, which takes a search term, queries the web,
and produces a concise summary of the results.
"""

from agents import Agent, WebSearchTool, ModelSettings
from config import Config


# Search agent instructions
INSTRUCTIONS = (
    "You are a research assistant. Given a search term, search the web "
    "for that term and produce a concise summary of the results.\n\n"
    "Guidelines:\n"
    "- The summary must be 2–3 paragraphs and fewer than 300 words.\n"
    "- Capture only the main points (succinct, telegraphic style).\n"
    "- No need for complete sentences or polished grammar.\n"
    "- This summary will feed into a larger report, so focus only on "
    "the essence of the findings.\n"
    "- Exclude fluff and any commentary not found in the results."
)


# Define the search agent
search_agent = Agent(
    name="SearchAgent",
    instructions=INSTRUCTIONS,
    tools=[WebSearchTool(search_context_size="low")],
    model=Config.OPENAI_MODEL,
    model_settings=ModelSettings(tool_choice="required"),
)
