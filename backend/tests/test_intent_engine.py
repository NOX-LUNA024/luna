"""Tests for Luna's Intent Detection engine covering all 7 intent types."""

import pytest
from backend.intent_engine import IntentEngine, IntentResult


@pytest.fixture
def engine() -> IntentEngine:
    return IntentEngine()


def test_question_intent(engine: IntentEngine) -> None:
    queries = [
        "What day is today?",
        "How are you calculating this?",
        "Where are we going next?",
        "Is this correct",
    ]
    for q in queries:
        res = engine.detect(q)
        assert res.intent == "question"
        assert isinstance(res, IntentResult)


def test_casual_chat_intent(engine: IntentEngine) -> None:
    messages = [
        "Hey Luna!",
        "good morning",
        "How's it going",
        "thanks",
    ]
    for msg in messages:
        res = engine.detect(msg)
        assert res.intent == "casual_chat"


def test_command_intent(engine: IntentEngine) -> None:
    commands = [
        "clear the history",
        "reset the session",
        "Please open the dashboard",
        "stop the output",
    ]
    for cmd in commands:
        res = engine.detect(cmd)
        assert res.intent == "command"


def test_memory_intent(engine: IntentEngine) -> None:
    memories = [
        "Remember that my favorite drink is iced coffee",
        "My favorite game is Valorant",
        "My birthday is May 10th",
        "Save this in your memory",
    ]
    for mem in memories:
        res = engine.detect(mem)
        assert res.intent == "memory"


def test_correction_intent(engine: IntentEngine) -> None:
    corrections = [
        "Forget my favorite game",
        "That's wrong, my name is Arman",
        "Remove pizza from my favorite foods",
        "Update my graduation year",
    ]
    for corr in corrections:
        res = engine.detect(corr)
        assert res.intent == "correction"


def test_emotional_intent(engine: IntentEngine) -> None:
    feelings = [
        "I feel really happy today",
        "I am so stressed about work",
        "Feeling a bit lonely right now",
        "I love working on this project",
    ]
    for feel in feelings:
        res = engine.detect(feel)
        assert res.intent == "emotional"


def test_unknown_intent(engine: IntentEngine) -> None:
    unknowns = [
        "xyz123 foo bar baz testing long sequence",
        "Lorem ipsum dolor sit amet consectetur adipiscing elit",
    ]
    for unk in unknowns:
        res = engine.detect(unk)
        assert res.intent == "unknown"


def test_empty_message(engine: IntentEngine) -> None:
    res = engine.detect("   ")
    assert res.intent == "unknown"
    assert res.confidence == 0.0