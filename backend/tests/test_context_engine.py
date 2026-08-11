"""Tests for Luna's ContextEngine."""

from __future__ import annotations

from backend.context_engine import ContextEngine, ContextResult


def test_select_context_relevant_memory():
    engine = ContextEngine()
    memories = {
        "favorites": {
            "games": ["Zelda", "Pokémon"],
            "foods": ["Pizza"],
        },
        "personal": {
            "name": "Arman",
        },
    }
    history = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi Arman!"},
    ]

    result = engine.select_context("What games do I like?", memories, history)

    assert isinstance(result, ContextResult)
    assert "favorites" in result.relevant_memories
    assert "games" in result.relevant_memories["favorites"]
    assert "foods" not in result.relevant_memories.get("favorites", {})
    assert len(result.recent_history) == 2


def test_select_context_history_slicing():
    engine = ContextEngine()
    memories = {}
    history = [{"role": "user", "content": f"msg {i}"} for i in range(10)]

    result = engine.select_context("tell me a story", memories, history, max_history=3)

    assert len(result.recent_history) == 3
    assert result.recent_history[0]["content"] == "msg 7"
    assert result.recent_history[-1]["content"] == "msg 9"