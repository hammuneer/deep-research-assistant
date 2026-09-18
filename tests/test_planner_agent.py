from deep_research.agents.planner_agent import WebSearchItem, WebSearchPlan


def test_receiver_email_defaults_to_none():
    plan = WebSearchPlan(searches=[WebSearchItem(reason="why", query="what")])

    assert plan.receiver_email is None


def test_receiver_email_can_be_provided():
    plan = WebSearchPlan(
        searches=[WebSearchItem(reason="why", query="what")],
        receiver_email="someone@example.com",
    )

    assert plan.receiver_email == "someone@example.com"
