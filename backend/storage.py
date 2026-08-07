"""Small, concurrency-safe JSON store for Luna's persistent memory."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)


class JsonStore:
    """Keeps JSON data in memory and persists it atomically on each mutation."""

    def __init__(self, path: Path, default: Any) -> None:
        self.path = path
        self.default = default
        self.data: Any = self._load()
        self._lock = asyncio.Lock()

    def _load(self) -> Any:
        try:
            with self.path.open("r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            return self.default
        except (json.JSONDecodeError, OSError):
            logger.exception("Unable to load JSON store: %s", self.path)
            return self.default

    async def save(self) -> None:
        """Atomically replace the data file, avoiding partially written JSON."""
        async with self._lock:
            await self._save_locked()

    async def set_value(self, key: str, value: str) -> None:
        """Update one memory entry and persist it while holding the write lock."""
        async with self._lock:
            self.data[key] = value
            await self._save_locked()

    async def replace(self, data: Any) -> None:
        """Atomically replace the whole document for coordinated state updates."""
        async with self._lock:
            self.data = data
            await self._save_locked()

    async def update(self, mutator: Callable[[Any], Any]) -> None:
        """Apply a synchronous transformation while holding the write lock."""
        async with self._lock:
            self.data = mutator(self.data)
            await self._save_locked()

    async def delete_value(self, key: str) -> bool:
        """Delete one entry atomically, returning whether it existed."""
        async with self._lock:
            if key not in self.data:
                return False
            del self.data[key]
            await self._save_locked()
            return True

    async def _save_locked(self) -> None:
        snapshot = json.dumps(self.data, indent=2, ensure_ascii=False)
        await asyncio.to_thread(self._write_atomic, snapshot)

    def _write_atomic(self, snapshot: str) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_path = tempfile.mkstemp(
            dir=self.path.parent, prefix=f".{self.path.name}.", suffix=".tmp"
        )
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as file:
                file.write(snapshot)
            os.replace(temporary_path, self.path)
        except Exception:
            try:
                os.unlink(temporary_path)
            except OSError:
                pass
            raise
