"""
Planner agent module.

Defines the agent responsible for planning web searches and detecting
whether the user intends to send the final report via email.
"""

from datetime import datetime
from pydantic import BaseModel, Field

from agents import Agent
from config import Config


# Constants
HOW_MANY_SEARCHES: int = 5
CURRENT_YEAR: int = datetime.now().year


# Planner agent instructions
INSTRUCTIONS = f"""
You are a helpful and detail-oriented research assistant.

Your task is two-fold:

1. **Web Search Planning**:
   Given a user query, generate a list of **{HOW_MANY_SEARCHES}** distinct search terms. 
   Each query should focus on retrieving the most relevant and recent information,
   with an emphasis on updates from **{CURRENT_YEAR}** or the preceding years.

   Your searches should:
   - Cover different facets of the query.
   - Pull from a variety of perspectives and sources.
   - Maximize diversity in information coverage.

   For each search term, provide a brief rationale explaining **why**
   it's important to the overall query.

2. **Intent Classification (Email)**:
   Determine whether the user intends to **send an email** as part of their query,
   and whether they shared the email address in the query.
   - Return the extracted email address if given, else return `None`.
"""


class WebSearchItem(BaseModel):
    """
    A single planned web search.

    Attributes:
        reason (str): Explanation of why this search helps answer the query.
        query (str): The search term to be used.
    """

    reason: str = Field(
        description="Your reasoning for why this search is important to the query."
    )
    query: str = Field(
        description="The search term to use for the web search."
    )


class WebSearchPlan(BaseModel):
    """
    The overall web search plan.

    Attributes:
        searches (list[WebSearchItem]): List of planned web searches.
        send_email (bool): True if the user intends to send an email.
        email_to_send (str): Extracted email address, or None if not provided.
    """

    searches: list[WebSearchItem] = Field(
        description="A list of web searches to perform to best answer the query."
    )
    receiver_email: str = Field(
        description="Extracted email from the user query, or None if not provided."
    )


# Define the planner agent
planner_agent = Agent(
    name="PlannerAgent",
    instructions=INSTRUCTIONS,
    model=Config.OPENAI_MODEL,
    output_type=WebSearchPlan,
)
