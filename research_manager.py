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
from agents import Runner, trace, gen_trace_id
from user_agents.search_agent import search_agent
from user_agents.planner_agent import planner_agent, WebSearchItem, WebSearchPlan
from user_agents.writer_agent import writer_agent, ReportData
from user_agents.email_agent import email_agent
from user_agents.email_agent import send_email

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
            print(
                f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}"
            )
            yield (
                f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}"
            )

            print("Starting research...")
            search_plan = await self.plan_searches(query)
            # print("Printing Search Plan for Debugging: \n\n", search_plan)
            yield "Searches planned, starting to search..."
            search_results = await self.perform_searches(search_plan)
            # print("Printing Search Results for Debugging: \n\n", search_results)
            yield "Searches complete, writing report..."
            report = await self.write_report(query, search_results)
            # print("Printing report for Debugging: \n\n", report)
            yield "Report written, sending email..."

            if  search_plan.receiver_email:
                receiver_email = search_plan.receiver_email
                # print("Printing receiver_email for Debugging: \n\n", receiver_email)
                await self.send_email(receiver_email, report)
                yield "Email sent, research complete"
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
        print("Planning searches...")
        result = await Runner.run(planner_agent, f"Query: {query}")
        print(f"Will perform {len(result.final_output.searches)} searches")
        return result.final_output_as(WebSearchPlan)

    async def perform_searches(self, search_plan: WebSearchPlan) -> list[str]:
        """
        Perform the searches defined in the plan.

        Args:
            search_plan (WebSearchPlan): The search plan.

        Returns:
            list[str]: Summaries of the search results.
        """
        print("Searching...")
        tasks = [asyncio.create_task(self.search(item)) for item in search_plan.searches]
        results: list[str] = []

        for i, task in enumerate(asyncio.as_completed(tasks), start=1):
            result = await task
            if result:
                results.append(result)
            print(f"Searching... {i}/{len(tasks)} completed")

        print("Finished searching")
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
        print("Thinking about report...")
        input_text = (
            f"Original query: {query}\nSummarized search results: {search_results}"
        )
        result = await Runner.run(writer_agent, input_text)
        print("Finished writing report")
        return result.final_output_as(ReportData)

    async def send_email(self, receiver_email: str, report: ReportData) -> None:
        """
        Send the research report via email.

        Args:
            receiver_email (str): The recipient email address.
            report (ReportData): The generated report to send.
        """
        print("Writing email...")

        input_text = f"""
        Receiver email: {receiver_email}
        Subject: Research Report on requested topic
        Report:
        {report.markdown_report}
        """

        await Runner.run(email_agent, input_text)
        # send_email(receiver_email, "Research Report on requested topic", report.markdown_report)
        print("Email sent")
