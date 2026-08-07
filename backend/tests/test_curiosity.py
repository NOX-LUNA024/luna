"""Offline tests for Luna's local curiosity engine."""

import asyncio

from backend.curiosity import CuriosityEngine
from backend.storage import JsonStore


def test_curiosity_persists_one_pending_topic_and_completes_it(tmp_path) -> None:
    memory_store = JsonStore(tmp_path / "memory.json", {"favorite game": "The Legend of Zelda"})
    engine = CuriosityEngine(tmp_path / "curiosity.json", memory_store)

    assert asyncio.run(engine.maybe_follow_up("Nice day.", [])) is None
    assert asyncio.run(engine.maybe_follow_up("I feel good.", [])) is None
    question = asyncio.run(engine.maybe_follow_up("I have some free time.", []))
    assert question == "What do you enjoy most about The Legend of Zelda, Arman?"
    assert engine.store.data["pending"]["key"] == "favorite_game_detail"
    assert asyncio.run(engine.maybe_follow_up("Another thought.", [])) is None

    asyncio.run(engine.mark_answered("I love the exploration."))
    restarted = CuriosityEngine(tmp_path / "curiosity.json", memory_store)
    assert restarted.store.data["pending"] is None
    assert "favorite_game_detail" in restarted.store.data["completed"]


def test_curiosity_does_not_interrupt_questions_or_repeat_completed_topics(tmp_path) -> None:
    memory_store = JsonStore(tmp_path / "memory.json", {"favorite game": "The Legend of Zelda"})
    engine = CuriosityEngine(tmp_path / "curiosity.json", memory_store)
    assert asyncio.run(engine.maybe_follow_up("How are you?", [])) is None
    asyncio.run(engine.store.replace({
        "pending": None, "completed": ["favorite_game_detail"], "turns_since_question": 2,
    }))
    assert asyncio.run(engine.maybe_follow_up("I am coding today.", [])) == (
        "What part would you like to make progress on next, Arman?"
    )
    assert asyncio.run(engine.maybe_follow_up("I am worried about this.", [])) is None
