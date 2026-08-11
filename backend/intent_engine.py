"""Simple, deterministic intent detection engine for Luna."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal


IntentType = Literal[
    "question",
    "casual_chat",
    "command",
    "memory",
    "correction",
    "emotional",
    "unknown",
]


@dataclass(frozen=True)
class IntentResult:
    """Structured result containing the detected intent and metadata."""

    intent: IntentType
    confidence: float
    raw_message: str


class IntentEngine:
    """Classifies user messages into primary intent categories."""

    # Emotional expressions
    EMOTIONAL_PATTERNS = [
        r"\b(sad|happy|angry|lonely|depressed|excited|anxious|stressed|tired|overwhelmed|hurt|feel|feeling)\b",
        r"\b(i'm feeling|i feel)\b",
        r"\bi love\s+(working|building|learning|spending|being|doing|this|that|you)\b",
    ]

    # Memory corrections
    CORRECTION_PATTERNS = [
        r"\b(forget|remove|delete|update|change|incorrect|wrong|not my|that's wrong|that's not)\b",
        r"\b(don't remember|stop remembering)\b",
    ]

    # Memory additions
    MEMORY_PATTERNS = [
        r"\b(remember that|keep in mind|note that|save this)\b",
        r"\bmy (favorite|birthday|name|nickname) is\b",
        r"\b(i really like|i really love|i love playing|i love eating|my favorite)\b",
    ]

    # Commands
    COMMAND_PATTERNS = [
        r"^(do|run|execute|open|close|start|stop|clear|set|reset|show|list)\b",
        r"\b(can you|please)\s+(do|run|open|close|start|stop|clear|set|reset)\b",
    ]

    # Casual chat
    # Anchored with ^ and $ so "How are you calculating this?"
    # does NOT get mistaken for casual chat.
    CASUAL_PATTERNS = [
        r"^(hi|hello|hey|heyya|hola|sup|yo|greetings)[!.]?$",
        r"^(good morning|good afternoon|good evening|good night)[!.]?$",
        r"^(how's it going|what's up|bye|see ya|cya|thanks|thank you)[!.]?$",
        r"^how are you[!.]?$",
    ]

    # Question starters
    QUESTION_STARTERS = (
        "what ",
        "why ",
        "how ",
        "when ",
        "where ",
        "who ",
        "which ",
        "is ",
        "are ",
        "can ",
        "could ",
        "would ",
    )

    def detect(self, message: str) -> IntentResult:
        """Analyze message text and return the primary detected intent."""

        clean_msg = message.strip()

        if not clean_msg:
            return IntentResult(
                intent="unknown",
                confidence=0.0,
                raw_message=message,
            )

        lowered = clean_msg.casefold()

        # 1. Correction
        for pattern in self.CORRECTION_PATTERNS:
            if re.search(pattern, lowered):
                return IntentResult(
                    intent="correction",
                    confidence=0.9,
                    raw_message=message,
                )

        # 2. Emotional
        for pattern in self.EMOTIONAL_PATTERNS:
            if re.search(pattern, lowered):
                return IntentResult(
                    intent="emotional",
                    confidence=0.85,
                    raw_message=message,
                )

        # 3. Memory
        for pattern in self.MEMORY_PATTERNS:
            if re.search(pattern, lowered):
                return IntentResult(
                    intent="memory",
                    confidence=0.9,
                    raw_message=message,
                )

        # 4. Command
        for pattern in self.COMMAND_PATTERNS:
            if re.search(pattern, lowered):
                return IntentResult(
                    intent="command",
                    confidence=0.85,
                    raw_message=message,
                )

        # 5. Explicit casual chat
        for pattern in self.CASUAL_PATTERNS:
            if re.search(pattern, lowered):
                return IntentResult(
                    intent="casual_chat",
                    confidence=0.8,
                    raw_message=message,
                )

        # 6. Question
        if lowered.endswith("?") or lowered.startswith(self.QUESTION_STARTERS):
            return IntentResult(
                intent="question",
                confidence=0.8,
                raw_message=message,
            )

        # 7. Short conversational fallback
        if len(lowered.split()) <= 3:
            return IntentResult(
                intent="casual_chat",
                confidence=0.5,
                raw_message=message,
            )

        # 8. Unknown
        return IntentResult(
            intent="unknown",
            confidence=0.3,
            raw_message=message,
        )