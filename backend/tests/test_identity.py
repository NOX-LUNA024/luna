"""Offline tests for Luna's persistent identity core."""

import asyncio

from backend.identity import IdentityCore


def test_identity_persists_and_is_available_to_the_prompt(tmp_path) -> None:
    core = IdentityCore(tmp_path / "identity.json", tmp_path / "relationship.json")
    asyncio.run(core.identity_store.set_value("mission", "To grow alongside Arman."))
    restarted = IdentityCore(tmp_path / "identity.json", tmp_path / "relationship.json")
    assert "Birthday: 5 August" in restarted.prompt_context()
    assert "Creator: Arman" in restarted.prompt_context()
    assert "To grow alongside Arman." in restarted.prompt_context()


def test_relationship_updates_and_milestones_are_persistent(tmp_path) -> None:
    core = IdentityCore(tmp_path / "identity.json", tmp_path / "relationship.json")
    asyncio.run(core.record_interaction(memory_count=1, saved_memory=True))
    for _ in range(9):
        asyncio.run(core.record_interaction(memory_count=1))

    restarted = IdentityCore(tmp_path / "identity.json", tmp_path / "relationship.json")
    relationship = restarted.relationship_store.data
    assert relationship["conversation_count"] == 10
    assert relationship["memory_count"] == 1
    milestone_keys = {milestone["key"] for milestone in relationship["major_milestones"]}
    assert {"first_conversation", "first_memory", "conversations_10"} <= milestone_keys
