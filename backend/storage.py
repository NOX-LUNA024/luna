"""Small, concurrency-safe JSON store for Luna's persistent memory."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Any, Callable, Sequence

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
        """Atomically replace the data file."""
        async with self._lock:
            await self._save_locked()

    async def set_value(self, key: str, value: Any) -> None:
        """Update one top-level entry and persist it."""
        async with self._lock:
            if not isinstance(self.data, dict):
                self.data = {}

            self.data[key] = value
            await self._save_locked()

    async def set_path(
        self,
        path: Sequence[str],
        value: Any,
    ) -> None:
        """Set a value inside a nested dictionary path."""
        if not path:
            raise ValueError("Memory path cannot be empty")

        async with self._lock:
            if not isinstance(self.data, dict):
                self.data = {}

            node = self.data

            for key in path[:-1]:
                child = node.get(key)

                if not isinstance(child, dict):
                    child = {}
                    node[key] = child

                node = child

            node[path[-1]] = value
            await self._save_locked()

    async def replace(self, data: Any) -> None:
        """Atomically replace the whole document."""
        async with self._lock:
            self.data = data
            await self._save_locked()

    async def update(self, mutator: Callable[[Any], Any]) -> None:
        """Apply a synchronous transformation while holding the write lock."""
        async with self._lock:
            self.data = mutator(self.data)
            await self._save_locked()

    async def delete_value(self, key: str) -> bool:
        """Delete one top-level entry atomically."""
        async with self._lock:
            if not isinstance(self.data, dict) or key not in self.data:
                return False

            del self.data[key]
            await self._save_locked()
            return True

    async def delete_path(self, path: Sequence[str]) -> bool:
        """Delete a nested value atomically."""
        if not path:
            return False

        async with self._lock:
            if not isinstance(self.data, dict):
                return False

            node = self.data

            for key in path[:-1]:
                node = node.get(key)

                if not isinstance(node, dict):
                    return False

            if path[-1] not in node:
                return False

            del node[path[-1]]
            await self._save_locked()
            return True

    def get_path(
        self,
        path: Sequence[str],
        default: Any = None,
    ) -> Any:
        """Read a nested value without modifying the store."""
        if not path:
            return default

        node = self.data

        for key in path:
            if not isinstance(node, dict) or key not in node:
                return default

            node = node[key]

        return node

    async def _save_locked(self) -> None:
        snapshot = json.dumps(
            self.data,
            indent=2,
            ensure_ascii=False,
        )

        await asyncio.to_thread(
            self._write_atomic,
            snapshot,
        )

    def _write_atomic(self, snapshot: str) -> None:
        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        descriptor, temporary_path = tempfile.mkstemp(
            dir=self.path.parent,
            prefix=f".{self.path.name}.",
            suffix=".tmp",
        )

        try:
            with os.fdopen(
                descriptor,
                "w",
                encoding="utf-8",
            ) as file:
                file.write(snapshot)

            os.replace(
                temporary_path,
                self.path,
            )

        except Exception:
            try:
                os.unlink(temporary_path)
            except OSError:
                pass

            raise