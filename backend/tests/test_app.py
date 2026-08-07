"""Offline API tests; no test makes a request to an AI provider."""

from __future__ import annotations

import asyncio
import sys
from types import SimpleNamespace
from pathlib import Path

from fastapi.testclient import TestClient

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from backend import main  # noqa: E402
from backend.storage import JsonStore  # noqa: E402

client = TestClient(main.app)


def test_home_and_state_are_available() -> None:
    assert client.get("/").status_code == 200
    state = client.get("/luna/state")
    assert state.status_code == 200
    assert {"greeting", "sky_phase", "thought", "story", "memories"} <= state.json().keys()


def test_chat_request_validation_rejects_blank_and_invalid_sessions() -> None:
    assert client.post("/chat/stream", json={"message": "   "}).status_code == 422
    response = client.post("/chat/stream", json={"message": "hello", "session_id": "bad id!"})
    assert response.status_code == 422


def test_memory_admin_requires_authentication() -> None:
    assert client.get("/admin/memory").status_code == 404


async def collect_stream(generator):
    return "".join([event async for event in generator])


def test_birthday_memory_survives_restart_and_is_available_to_luna(tmp_path) -> None:
    original_store, original_client = main.memory_store, main.client
    memory_file = tmp_path / "memory.json"
    try:
        main.memory_store = JsonStore(memory_file, {})
        confirmation = asyncio.run(
            collect_stream(main.luna_response_generator("My birthday is 10 October.", "test"))
        )
        assert "I'll remember that, Arman: your birthday is 10 October." in confirmation
        assert JsonStore(memory_file, {}).data == {"birthday": "10 October"}
        asyncio.run(collect_stream(main.luna_response_generator("My birthday is 10 October.", "test")))
        assert JsonStore(memory_file, {}).data == {"birthday": "10 October"}

        main.memory_store = JsonStore(memory_file, {})  # Simulates backend restart.
        prompt = main.build_system_prompt()
        assert '"birthday": "10 October"' in prompt
        assert "Your birthday is 5 August." in prompt

        captured_messages = []

        class FakeCompletions:
            async def create(self, *, messages, **_kwargs):
                captured_messages.extend(messages)

                async def stream():
                    yield SimpleNamespace(
                        choices=[SimpleNamespace(delta=SimpleNamespace(content="Your birthday is 10 October."))]
                    )

                return stream()

        main.client = SimpleNamespace(chat=SimpleNamespace(completions=FakeCompletions()))
        recall = asyncio.run(
            collect_stream(main.luna_response_generator("When is my birthday?", "test"))
        )
        assert "Your birthday is 10 October, Arman. I remember." in recall
        assert captured_messages == []

        asyncio.run(main.memory_store.set_value("favorite colors", "Blue and Black"))
        asyncio.run(main.memory_store.set_value("luna birthday", "5 August"))
        color_recall = asyncio.run(
            collect_stream(main.luna_response_generator("What's my favorite color?", "test"))
        )
        luna_birthday_recall = asyncio.run(
            collect_stream(main.luna_response_generator("When is Luna's birthday?", "test"))
        )
        assert "Your favorite colors are Blue and Black, Arman." in color_recall
        assert "My birthday is on 5 August." in luna_birthday_recall
    finally:
        main.memory_store, main.client = original_store, original_client
