"""
Research Manager module.

This module defines the ResearchManager class, which orchestrates the
end-to-end research workflow:

1. Plan searches
2. Perform searches
3. Write a report
4. Optionally send the report via email
"""

import asyncio
import logging
import re

from agents import Runner, gen_trace_id, trace

from deep_research.agents.email_agent import email_agent
from deep_research.agents.planner_agent import WebSearchItem, WebSearchPlan, planner_agent
from deep_research.agents.search_agent import search_agent
from deep_research.agents.writer_agent import ReportData, writer_agent

logger = logging.getLogger(__name__)

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ResearchManager:
    """Coordinates the multi-step research process."""

    async def run(self, query: str):
        """
        Run the deep research process.

        Args:
            query (str): The research topic provided by the user.

        Yields:
            str: Status updates and the final report as markdown.
        """
        trace_id = gen_trace_id()
        with trace("Research trace", trace_id=trace_id):
            trace_url = f"https://platform.openai.com/traces/trace?trace_id={trace_id}"
            logger.info("View trace: %s", trace_url)
            yield f"View trace: {trace_url}"

            logger.info("Starting research for query: %r", query)
            search_plan = await self.plan_searches(query)
            yield "Searches planned, starting to search..."
            search_results = await self.perform_searches(search_plan)
            yield "Searches complete, writing report..."
            report = await self.write_report(query, search_results)
            yield "Report written, sending email..."

            receiver_email = search_plan.receiver_email
            if receiver_email and EMAIL_PATTERN.match(receiver_email):
                await self.send_email(receiver_email, report)
                yield "Email sent, research complete"
            elif receiver_email:
                logger.warning("Skipping email send: %r is not a valid email address", receiver_email)
                yield "Skipping email send: the extracted address didn't look valid"
            else:
                yield "Skipping email send, as not required..."

            yield report.markdown_report

    async def plan_searches(self, query: str) -> WebSearchPlan:
        """
        Plan the searches to perform for the query.

        Args:
            query (str): The research topic.

        Returns:
            WebSearchPlan: The search plan with queries and optional email info.
        """
        logger.info("Planning searches...")
        result = await Runner.run(planner_agent, f"Query: {query}")
        plan = result.final_output_as(WebSearchPlan)
        logger.info("Will perform %d searches", len(plan.searches))
        return plan

    async def perform_searches(self, search_plan: WebSearchPlan) -> list[str]:
        """
        Perform the searches defined in the plan.

        Args:
            search_plan (WebSearchPlan): The search plan.

        Returns:
            list[str]: Summaries of the search results.
        """
        logger.info("Searching...")
        tasks = [asyncio.create_task(self.search(item)) for item in search_plan.searches]
        results: list[str] = []

        for i, task in enumerate(asyncio.as_completed(tasks), start=1):
            result = await task
            if result:
                results.append(result)
            logger.info("Searching... %d/%d completed", i, len(tasks))

        logger.info("Finished searching")
        return results

    async def search(self, item: WebSearchItem) -> str | None:
        """
        Perform a single web search.

        Args:
            item (WebSearchItem): The search item containing query and rationale.

        Returns:
            str | None: The search result summary, or None if failed.
        """
        input_text = f"Search term: {item.query}\nReason for searching: {item.reason}"
        try:
            result = await Runner.run(search_agent, input_text)
            return str(result.final_output)
        except Exception:
            logger.exception("Search failed for term: %r", item.query)
            return None

    async def write_report(self, query: str, search_results: list[str]) -> ReportData:
        """
        Generate a detailed report from search results.

        Args:
            query (str): The original research query.
            search_results (list[str]): The search summaries.

        Returns:
            ReportData: The generated report data.
        """
        logger.info("Thinking about report...")
        input_text = f"Original query: {query}\nSummarized search results: {search_results}"
        result = await Runner.run(writer_agent, input_text)
        logger.info("Finished writing report")
        return result.final_output_as(ReportData)

    async def send_email(self, receiver_email: str, report: ReportData) -> None:
        """
        Send the research report via email.

        Args:
            receiver_email (str): The recipient email address.
            report (ReportData): The generated report to send.
        """
        logger.info("Writing email...")
        input_text = f"""
        Receiver email: {receiver_email}
        Subject: Research Report on requested topic
        Report:
        {report.markdown_report}
        """
        await Runner.run(email_agent, input_text)
        logger.info("Email sent")
