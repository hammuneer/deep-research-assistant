from unittest.mock import AsyncMock

from deep_research.agents.planner_agent import WebSearchPlan
from deep_research.agents.writer_agent import ReportData
from deep_research.research_manager import ResearchManager


def _make_manager(receiver_email):
    manager = ResearchManager()
    manager.plan_searches = AsyncMock(return_value=WebSearchPlan(searches=[], receiver_email=receiver_email))
    manager.perform_searches = AsyncMock(return_value=[])
    manager.write_report = AsyncMock(
        return_value=ReportData(short_summary="s", markdown_report="report", follow_up_questions=[])
    )
    manager.send_email = AsyncMock()
    return manager


async def _collect(manager, query="topic"):
    return [chunk async for chunk in manager.run(query)]


async def test_sends_email_when_receiver_email_is_valid():
    manager = _make_manager("someone@example.com")

    chunks = await _collect(manager)

    manager.send_email.assert_awaited_once()
    assert any("Email sent" in c for c in chunks)


async def test_skips_email_when_no_receiver_email():
    manager = _make_manager(None)

    chunks = await _collect(manager)

    manager.send_email.assert_not_awaited()
    assert any("Skipping email send, as not required" in c for c in chunks)


async def test_skips_email_when_receiver_email_is_malformed():
    manager = _make_manager("not-an-email")

    chunks = await _collect(manager)

    manager.send_email.assert_not_awaited()
    assert any("didn't look valid" in c for c in chunks)
