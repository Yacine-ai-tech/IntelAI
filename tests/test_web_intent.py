import pytest

from src.services.web_intent import plan_web

pytestmark = pytest.mark.unit

HISTORY = [{"role": "user", "content": "Tell me about Anthropic"}]


@pytest.mark.parametrize("question", [
    "Who is OpenAI and what do they do?",
    "Tell me about Acme Corp",
    "Compare Stripe and Adyen",
    "What are the latest GDPR rules?",
    "How do we compare to industry benchmarks for churn?",
    "Qui est le PDG de Danone ?",
])
def test_external_questions_search_the_web(question):
    assert plan_web(question, HISTORY).enabled


@pytest.mark.parametrize("question", [
    "What is our gross margin this quarter?",
    "Résume nos KPIs",
    "hi",
    "How many employees do we have?",
])
def test_internal_questions_skip_the_web(question):
    assert not plan_web(question, HISTORY).enabled


def test_explicit_request_wins_and_strips_the_framing():
    plan = plan_web("do a web search on Tesla headquarters", [])
    assert plan.mode == "explicit"
    assert plan.query == "Tesla headquarters"


def test_explicit_french_request():
    plan = plan_web("cherche sur le web les derniers chiffres de Danone", [])
    assert plan.mode == "explicit" and "Danone" in plan.query


def test_explicit_request_without_topic_uses_previous_question():
    plan = plan_web("search the web", HISTORY)
    assert plan.mode == "explicit" and "Anthropic" in plan.query
