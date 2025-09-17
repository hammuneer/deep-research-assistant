"""
Writer agent module.

This module defines the WriterAgent, which is responsible for synthesizing
a comprehensive research report. It takes the original query and summaries
from earlier research, then produces a detailed, cohesive document in markdown.

The report should:
- Begin with a logical outline of structure and flow.
- Provide detailed sections that expand on the findings.
- Conclude with a summary and suggested follow-up research questions.
"""

from pydantic import BaseModel, Field
from agents import Agent
from config import Config


# Writer agent instructions
INSTRUCTIONS = (
    "You are a senior researcher tasked with writing a cohesive report "
    "for a research query. You will be provided with the original query, "
    "along with research summaries prepared by an assistant.\n\n"
    "Your responsibilities include:\n"
    "1. Drafting an outline that shows how the report will be structured.\n"
    "2. Expanding the outline into a full report that integrates the findings.\n"
    "3. Writing in markdown format with proper headings, lists, and emphasis "
    "where appropriate.\n\n"
    "The final report should be extensive and detailed, aiming for a length "
    "equivalent to 5–10 pages (at least 1000 words)."
)


class ReportData(BaseModel):
    """
    Data model for the research report.

    Attributes:
        short_summary (str): A concise 2–3 sentence overview of the main findings.
        markdown_report (str): The complete research report in markdown format.
        follow_up_questions (list[str]): Suggested topics or questions for future research.
    """

    short_summary: str = Field(
        description="A short 2–3 sentence summary of the findings."
    )

    markdown_report: str = Field(
        description="The final report, written in markdown format."
    )

    follow_up_questions: list[str] = Field(
        description="Suggested topics to research further."
    )


# Define the writer agent
writer_agent = Agent(
    name="WriterAgent",
    instructions=INSTRUCTIONS,
    model=Config.OPENAI_MODEL,
    output_type=ReportData,
)
