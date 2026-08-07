"""Local, predictable detection of personal facts worth remembering."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class MemoryCandidate:
    key: str
    value: str


# These phrases are deliberate statements about Arman, not guesses made by a
# provider. This keeps capture fast, private, and easy to reason about.
PERSONAL_FACT_PATTERNS = (
    re.compile(
        r"^\s*my\s+(birthday|name|favourite(?:\s+\w+)?|favorite(?:\s+\w+)?|"
        r"(?:cat|dog)'?s?\s+name)\s+is\s+(.+?)\s*[.!?]?\s*$",
        re.IGNORECASE,
    ),
    re.compile(r"^\s*i\s+(live\s+in|work\s+at|study)\s+(.+?)\s*[.!?]?\s*$", re.IGNORECASE),
)
EXPLICIT_MEMORY_PATTERN = re.compile(
    r"^\s*remember\s+that\s+my\s+(.+?)\s+is\s+(.+?)\s*[.!?]?\s*$", re.IGNORECASE
)


def extract_memory_candidate(message: str) -> MemoryCandidate | None:
    """Return a safe, bounded memory entry when the user states a personal fact."""
    match = EXPLICIT_MEMORY_PATTERN.match(message)
    if match:
        return _candidate(match.group(1), match.group(2))

    for pattern in PERSONAL_FACT_PATTERNS:
        match = pattern.match(message)
        if match:
            return _candidate(match.group(1), match.group(2))
    return None


def _candidate(key: str, value: str) -> MemoryCandidate | None:
    normalized_key = " ".join(key.casefold().split())[:100]
    # Keep regional spelling and singular/plural variants in one durable key.
    if normalized_key in {"favorite color", "favourite colour", "favourite color"}:
        normalized_key = "favorite colors"
    normalized_value = value.strip(" .!?")[:500]
    if not normalized_key or not normalized_value:
        return None
    return MemoryCandidate(key=normalized_key, value=normalized_value)
