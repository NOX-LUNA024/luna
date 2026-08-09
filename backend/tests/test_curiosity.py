import pytest
from pathlib import Path

from backend.curiosity import CuriosityEngine


class DummyStore:
    def __init__(self, data):
        self.data = data


@pytest.mark.asyncio
async def test_follow_up_favorite_game():
    memory_store = DummyStore(
        {"favorites": {"games": ["The Legend of Zelda"]}}
    )

    engine = CuriosityEngine(
        path=Path("dummy_path"),
        memory_store=memory_store,
    )

    question = engine._select_topic([], "What's up?", [])

    assert question == {
        "key": "favorite_game_detail",
        "question": "What do you enjoy most about The Legend of Zelda, Arman?",
    }


@pytest.mark.asyncio
async def test_maybe_follow_up_trigger(tmp_path):
    memory_store = DummyStore(
        {"favorites": {"games": ["The Legend of Zelda"]}}
    )

    engine = CuriosityEngine(
        path=tmp_path / "curiosity.json",
        memory_store=memory_store,
    )

    # Fast forward turn counter to meet MIN_TURNS_BETWEEN_QUESTIONS
    engine.store.data["turns_since_question"] = 2

    question = await engine.maybe_follow_up(
        "Just relaxing today.",
        [],
    )

    assert question == "What do you enjoy most about The Legend of Zelda, Arman?"