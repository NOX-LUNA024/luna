"""Offline tests for Luna Mind v1."""

import asyncio

from backend.mind import MindEngine


def test_mind_persists_emotion_reflections_and_one_daily_journal(tmp_path) -> None:
    engine = MindEngine(tmp_path / "emotion.json", tmp_path / "thoughts.json", tmp_path / "journal.json")
    asyncio.run(engine.record_interaction("I am excited to build a project!", "Let's begin."))
    asyncio.run(engine.record_interaction("My birthday is 24 May 2008.", "I'll remember.", ("birthday", "24 May 2008")))

    restarted = MindEngine(tmp_path / "emotion.json", tmp_path / "thoughts.json", tmp_path / "journal.json")
    assert restarted.emotion["mood"] == "calm"
    assert restarted.emotion["energy"] == 1
    assert len(restarted.thoughts_store.data) == 2
    assert len(restarted.journal_store.data) == 1
    entry = next(iter(restarted.journal_store.data.values()))
    assert "Remembered Arman's birthday: 24 May 2008." in entry["highlights"]
    assert "Private emotional context" in restarted.prompt_context()


def test_hidden_reflections_keep_only_the_latest_five(tmp_path) -> None:
    engine = MindEngine(tmp_path / "emotion.json", tmp_path / "thoughts.json", tmp_path / "journal.json")
    for number in range(6):
        asyncio.run(engine.record_interaction(f"Question {number}?", "Answer"))
    assert len(engine.thoughts_store.data) == 5
