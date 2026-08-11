"""Tests for Luna's Cognitive DecisionEngine covering key decision combinations."""

from __future__ import annotations

import pytest
from backend.decision_engine import DecisionEngine, DecisionResult


@pytest.fixture
def engine() -> DecisionEngine:
    return DecisionEngine()


@pytest.mark.parametrize(
    "intent, behavior, emotion, expected_mode",
    [
        ("question", "answer", "neutral", "answer"),
        ("casual_chat", "chat", "happy", "chat"),
        ("command", "execute", "neutral", "execute"),
        ("memory", "remember", "curious", "remember"),
        ("correction", "correct", "neutral", "correct"),
        ("emotional", "empathy", "sad", "empathy"),
        ("unknown", "general", "neutral", "general"),
    ],
)
def test_decision_engine_supported_combinations(
    engine: DecisionEngine,
    intent: str,
    behavior: str,
    emotion: str,
    expected_mode: str,
) -> None:
    result = engine.decide(intent=intent, behavior=behavior, emotion=emotion)

    assert isinstance(result, DecisionResult)
    assert result.intent == intent
    assert result.behavior == behavior
    assert result.response_mode == expected_mode


def test_decision_engine_emotional_intent_override(
    engine: DecisionEngine,
) -> None:
    result = engine.decide(intent="emotional", behavior="chat", emotion="sad")

    assert result.response_mode == "empathy"


def test_decision_engine_dict_emotion_support(
    engine: DecisionEngine,
) -> None:
    emotion_dict = {"mood": "happy", "intensity": 0.8}
    result = engine.decide(
        intent="casual_chat", behavior="chat", emotion=emotion_dict
    )

    assert result.response_mode == "chat"


def test_decision_engine_unknown_behavior_fallback(
    engine: DecisionEngine,
) -> None:
    result = engine.decide(
        intent="custom_intent", behavior="unknown_behavior", emotion=None
    )

    assert result.response_mode == "general"