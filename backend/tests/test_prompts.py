"""Tests for prompt template."""

from langchain_core.messages import HumanMessage, SystemMessage

from app.prompts import SYSTEM_PROMPT, build_prompt


def test_build_prompt_returns_messages():
    messages = build_prompt("some context", "some question")
    assert len(messages) == 2
    assert isinstance(messages[0], SystemMessage)
    assert isinstance(messages[1], HumanMessage)


def test_build_prompt_system_message_content():
    messages = build_prompt("ctx", "q")
    assert "HR Policy" in messages[0].content
    assert "Answer ONLY from the context" in messages[0].content


def test_build_prompt_human_message_contains_context_and_question():
    messages = build_prompt("my context here", "my question here")
    assert "my context here" in messages[1].content
    assert "my question here" in messages[1].content


def test_system_prompt_not_empty():
    assert len(SYSTEM_PROMPT) > 100
