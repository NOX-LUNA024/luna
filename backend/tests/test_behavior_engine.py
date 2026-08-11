"""Tests for Luna's deterministic BehaviorEngine covering all supported intents."""

from __future__ import annotations

import pytest
from backend.behavior_engine import BehaviorEngine, BehaviorResult


@pytest.fixture
def engine() -> BehaviorEngine:
    return BehaviorEngine()


@pytest.mark.parametrize(
    "intent, expected_behavior",
    [
        ("question", "answer"),
        ("casual_chat", "chat"),
        ("command", "execute"),
        ("memory", "remember"),
        ("correction", "correct"),
        ("emotional", "empathy"),
        ("unknown", "general"),
    ],
)
def test_behavior_engine_all_intents(
    engine: BehaviorEngine, intent: str, expected_behavior: str
) -> None:
    result = engine.evaluate(intent)

    assert isinstance(result, BehaviorResult)
    assert result.intent == intent
    assert result.behavior == expected_behavior


def test_behavior_engine_unrecognized_intent_fallback(
    engine: BehaviorEngine,
) -> None:
    result = engine.evaluate("unsupported_intent_type")

    assert result.intent == "unsupported_intent_type"
    assert result.behavior == "general"