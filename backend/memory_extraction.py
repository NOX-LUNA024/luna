"""Local, predictable detection of personal facts worth remembering."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class MemoryCandidate:
    key: str
    value: str


PERSONAL_FACT_PATTERNS = (
    re.compile(
        r"^\s*my\s+"
        r"(birthday|name|fav(?:ourite|orite)?(?:\s+\w+)?|"
        r"favourite(?:\s+\w+)?|favorite(?:\s+\w+)?|"
        r"(?:cat|dog)'?s?\s+name)"
        r"\s+is\s+(.+?)\s*[.!?]?\s*$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^\s*i\s+(live\s+in|work\s+at|study)\s+(.+?)\s*[.!?]?\s*$",
        re.IGNORECASE,
    ),
)


EXPLICIT_MEMORY_PATTERN = re.compile(
    r"^\s*remember(?:\s+that)?\s+my\s+(.+?)\s+is\s+(.+?)\s*[.!?]?\s*$",
    re.IGNORECASE,
)


LIKE_PATTERN = re.compile(
    r"^\s*i\s+(?:also\s+)?(like|love)\s+(.+?)\s*[.!?]?\s*$",
    re.IGNORECASE,
)


CALL_ME_PATTERN = re.compile(
    r"^\s*call\s+me\s+(.+?)\s*[.!?]?\s*$",
    re.IGNORECASE,
)


def extract_memory_candidate(message: str) -> MemoryCandidate | None:
    """Extract a predictable long-term memory candidate from a message."""

    message = message.strip()

    if not message:
        return None

    # Explicit memory request.
    match = EXPLICIT_MEMORY_PATTERN.match(message)
    if match:
        return _candidate(
            match.group(1),
            match.group(2),
        )

    # Direct personal facts.
    for pattern in PERSONAL_FACT_PATTERNS:
        match = pattern.match(message)

        if match:
            return _candidate(
                match.group(1),
                match.group(2),
            )

    # Likes / loves.
    match = LIKE_PATTERN.match(message)

    if match:
        thing = _clean_preference(match.group(2))

        if not thing:
            return None

        drinks = {
            "coffee",
            "tea",
            "juice",
            "milk",
        }

        games = {
            "cricket",
            "football",
            "badminton",
            "volleyball",
            "basketball",
        }

        movies = {
            "harry potter",
            "spider-man",
            "ms dhoni",
            "interstellar",
        }

        normalized_thing = thing.casefold()

        if normalized_thing in drinks:
            return _candidate(
                "favorite drink",
                thing,
            )

        if normalized_thing in games:
            return _candidate(
                "favorite game",
                thing,
            )

        if normalized_thing in movies:
            return _candidate(
                "favorite movie",
                thing,
            )

        return _candidate(
            "likes",
            thing,
        )

    # Nickname.
    match = CALL_ME_PATTERN.match(message)

    if match:
        return _candidate(
            "nickname",
            match.group(1),
        )

    return None


def _clean_preference(value: str) -> str:
    """Remove conversational filler from a preference value."""

    value = value.strip()

    # Remove common endings.
    value = re.sub(
        r"\s+(?:too|also|as\s+well)$",
        "",
        value,
        flags=re.IGNORECASE,
    )

    return value.strip(" .!?")


def _candidate(
    key: str,
    value: str,
) -> MemoryCandidate | None:
    """Normalize a detected memory into a stable key/value pair."""

    normalized_key = " ".join(
        key.casefold().split()
    )[:100]

    normalized_value = value.strip(" .!?")[:500]

    if not normalized_key or not normalized_value:
        return None

    normalized_key = normalized_key.replace(
        "fav ",
        "favorite ",
    )

    normalized_key = normalized_key.replace(
        "favourite ",
        "favorite ",
    )

    aliases = {
        "favorite color": "favorite colors",
        "favorite colour": "favorite colors",
        "favorite colours": "favorite colors",
        "fav color": "favorite colors",
        "fav colours": "favorite colors",
        "favorite games": "favorite game",
        "fav games": "favorite game",
        "favorite drinks": "favorite drink",
        "favorite movies": "favorite movie",
        "favorite animes": "favorite anime",
        "favorite songs": "favorite song",
    }

    normalized_key = aliases.get(
        normalized_key,
        normalized_key,
    )

    return MemoryCandidate(
        key=normalized_key,
        value=normalized_value,
    )