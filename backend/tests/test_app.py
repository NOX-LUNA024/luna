import pytest
from pathlib import Path
import backend.main as main
from backend.storage import JsonStore


@pytest.mark.asyncio
async def test_birthday_persistence(tmp_path: Path):
    memory_file = tmp_path / "memory.json"
    original_store = main.memory_store

    try:
        main.memory_store = JsonStore(memory_file, {})

        # Execute full response generator pipeline
        response_chunks = []
        async for chunk in main.luna_response_generator("My birthday is 10 October.", "test"):
            response_chunks.append(chunk)

        full_response = "".join(response_chunks)

        # Validate reply content matches expected confirmation
        assert "I'll remember that, Arman: your birthday is 10 October." in full_response

        # Validate structured memory persistence on disk
        assert JsonStore(memory_file, {}).data == {
            "personal": {
                "birthday": "10 October"
            }
        }
    finally:
        main.memory_store = original_store