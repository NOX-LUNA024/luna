"""Simple local context engine for selecting relevant memories and chat history."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ContextResult:
    relevant_memories: Dict[str, Any] = field(default_factory=dict)
    recent_history: List[Dict[str, str]] = field(default_factory=list)


class ContextEngine:
    """Luna's local context selector."""

    def select_context(
        self,
        message: str,
        memories: Dict[str, Any],
        history: List[Dict[str, str]],
        max_history: int = 5,
    ) -> ContextResult:
        """Select relevant memories based on keyword matching and slice recent history."""
        selected_memories: Dict[str, Any] = {}
        msg_words = set(re.findall(r"\w+", message.casefold()))

        if msg_words and isinstance(memories, dict):
            for category, data in memories.items():
                if isinstance(data, dict):
                    matched_items = {}
                    for k, v in data.items():
                        # Check if key or scalar value overlaps with prompt words
                        val_str = str(v).casefold()
                        if (
                            k.casefold() in msg_words
                            or any(w in msg_words for w in re.findall(r"\w+", val_str))
                        ):
                            matched_items[k] = v

                    if matched_items:
                        selected_memories[category] = matched_items
                else:
                    # Top-level non-dict values
                    val_str = str(data).casefold()
                    if (
                        category.casefold() in msg_words
                        or any(w in msg_words for w in re.findall(r"\w+", val_str))
                    ):
                        selected_memories[category] = data

        recent_history = history[-max_history:] if history else []

        return ContextResult(
            relevant_memories=selected_memories,
            recent_history=recent_history,
        )