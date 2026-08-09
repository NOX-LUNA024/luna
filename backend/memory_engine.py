from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Memory:
    key: str
    value: str
    category: str
    importance: int
    confidence: float = 1.0


class MemoryEngine:
    """Luna's long-term memory brain."""

    def process(self, message: str) -> Optional[Memory]:
        """Main entry point."""

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
        """Extract a possible memory from text."""

        message = message.strip()

        if not message:
            return None

        # TODO:
        # Detect:
        # - My favorite game is cricket
        # - My favorite movie is Interstellar
        # - I like coffee
        # - I love Harry Potter
        # - Call me Armu
        # - Remember my hobby is coding
        # - I'm from Nellore
        # - My dream is to build a startup
        # - I usually sleep at 3 AM
        # - My mom's name is Akhi
        #
        # Return:
        #
        # Memory(
        #     key="favorite_game",
        #     value="cricket",
        #     category="preference",
        #     importance=8
        # )

        return None

    def normalize(self, memory: Memory) -> Memory:
        """Normalize keys and values."""

        memory.key = memory.key.strip().casefold().replace(" ", "_")
        memory.value = memory.value.strip()

        return memory

    def classify(self, memory: Memory) -> str:
        """Determine the memory category."""

        return memory.category

    def score(self, memory: Memory) -> int:
        """Score memory importance from 1-10."""

        return memory.importance

    def should_save(self, memory: Memory) -> bool:
        """Decide whether to keep this memory."""

        return memory.importance >= 5

    def save(self, memory: Memory) -> None:
        """Save memory (implemented later)."""
        pass