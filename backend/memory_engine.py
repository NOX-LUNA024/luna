"""Luna's local, predictable long-term memory engine."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from .memory_extraction import extract_memory_candidate


@dataclass
class Memory:
    key: str
    value: str
    category: str
    importance: int
    confidence: float = 1.0


class MemoryEngine:
    """Luna's long-term memory brain."""

    CATEGORY_SCORES = {
        "identity": 9,
        "family": 9,
        "goal": 8,
        "preference": 7,
        "habit": 6,
        "location": 7,
        "fact": 6,
    }

    def process(self, message: str) -> Optional[Memory]:
        """Extract, normalize, classify, score, and validate a memory."""

        memory = self.extract(message)

        if memory is None:
            return None

        memory = self.normalize(memory)
        memory.category = self.classify(memory)
        memory.importance = self.score(memory)

        if not self.should_save(memory):
            return None

        return memory

    def extract(self, message: str) -> Optional[Memory]:
        """Extract a memory using Luna's existing local extractor."""

        message = message.strip()

        if not message:
            return None

        candidate = extract_memory_candidate(message)

        if candidate is None:
            return None

        return Memory(
            key=candidate.key,
            value=candidate.value,
            category="fact",
            importance=5,
        )

    def normalize(self, memory: Memory) -> Memory:
        """Normalize keys and values without changing their meaning."""

        memory.key = " ".join(
            memory.key.strip().casefold().split()
        )

        memory.value = " ".join(
            memory.value.strip().split()
        )

        memory.value = memory.value.strip(" .!?")

        return memory

    def classify(self, memory: Memory) -> str:
        """Determine the type of long-term memory."""

        key = memory.key.casefold()

        if key in {
            "name",
            "nickname",
            "birthday",
        }:
            return "identity"

        if key in {
            "mother",
            "mother name",
            "father",
            "father name",
            "brother",
            "brother name",
        }:
            return "family"

        if key.startswith("favorite "):
            return "preference"

        if key in {
            "likes",
            "hobby",
        }:
            return "preference"

        if key in {
            "sleep schedule",
            "wake schedule",
            "daily routine",
        }:
            return "habit"

        if key in {
            "live in",
            "location",
            "city",
            "country",
        }:
            return "location"

        if key in {
            "dream",
            "goal",
            "current project",
        }:
            return "goal"

        return "fact"

    def score(self, memory: Memory) -> int:
        """Calculate importance from category and key."""

        category_score = self.CATEGORY_SCORES.get(
            memory.category,
            5,
        )

        key = memory.key.casefold()

        # Especially important personal identity.
        if key in {
            "name",
            "nickname",
            "birthday",
        }:
            return 10

        # Important family information.
        if memory.category == "family":
            return 9

        # Goals/projects should remain strong memories.
        if memory.category == "goal":
            return 9

        return max(
            1,
            min(10, category_score),
        )

    def should_save(self, memory: Memory) -> bool:
        """Decide whether this memory deserves long-term storage."""

        if not memory.key or not memory.value:
            return False

        if memory.confidence < 0.60:
            return False

        return memory.importance >= 5

    def save(self, memory: Memory) -> None:
        """Persistence is handled by JsonStore/main.py."""

        # MemoryEngine decides WHAT should be remembered.
        # JsonStore decides HOW it is persisted.
        pass