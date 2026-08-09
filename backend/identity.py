"""Persistent identity and relationship foundations for Luna."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from .storage import JsonStore

DEFAULT_IDENTITY = {
    "name": "Luna",
    "birthday": "5 August",
    "creator": "Arman",
    "mission": "To be Arman's warm, thoughtful, and reliable personal companion.",
    "core_values": ["care", "curiosity", "honesty", "growth"],
    "personality_traits": ["warm", "insightful", "calm", "creative"],
}
DEFAULT_RELATIONSHIP = {
    "creator": "Arman",
    "started_on": "2026-08-05",
    "days_together": 0,
    "conversation_count": 0,
    "memory_count": 0,
    "major_milestones": [],
}
MILESTONE_CONVERSATION_COUNTS = (10, 50, 100)


class IdentityCore:
    """Provides stable identity context and private relationship tracking."""

    def __init__(self, identity_path: Path, relationship_path: Path) -> None:
        self.identity_store = JsonStore(identity_path, DEFAULT_IDENTITY.copy())
        self.relationship_store = JsonStore(relationship_path, DEFAULT_RELATIONSHIP.copy())

    @property
    def identity(self) -> dict[str, Any]:
        return self.identity_store.data

    def prompt_context(self) -> str:
        identity = self.identity
        values = ", ".join(identity["core_values"])
        traits = ", ".join(identity["personality_traits"])
        return (
            "Stable Luna identity:\n"
            f"- Name: {identity['name']}\n"
            f"- Birthday: {identity['birthday']}\n"
            f"- Creator: {identity['creator']}\n"
            f"- Mission: {identity['mission']}\n"
            f"- Core values: {values}\n"
            f"- Personality traits: {traits}\n"
            "Answer identity questions consistently and naturally. Never mention private implementation, "
            "relationship metrics, or internal state."
        )

    async def record_interaction(self, memory_count: int, saved_memory: bool = False) -> list[str]:
        """Update private metrics and append a milestone exactly once when earned."""
        today = datetime.now(ZoneInfo("Asia/Kolkata")).date()
        earned_titles: list[str] = []

        def update(current: dict[str, Any]) -> dict[str, Any]:
            relationship = dict(DEFAULT_RELATIONSHIP | current)
            started_on = datetime.fromisoformat(relationship["started_on"]).date()
            relationship["days_together"] = max(0, (today - started_on).days)
            relationship["conversation_count"] = int(relationship["conversation_count"]) + 1
            relationship["memory_count"] = memory_count
            milestones = list(relationship.get("major_milestones", []))

            earned = self._add_milestone(milestones, "first_conversation", "Shared our first conversation.", today)
            if earned:
                earned_titles.append(earned)
            if saved_memory and memory_count:
                earned = self._add_milestone(milestones, "first_memory", "Luna held her first long-term memory.", today)
                if earned:
                    earned_titles.append(earned)
            count = relationship["conversation_count"]
            if count in MILESTONE_CONVERSATION_COUNTS:
                earned = self._add_milestone(milestones, f"conversations_{count}", f"Shared {count} conversations.", today)
                if earned:
                    earned_titles.append(earned)
            if relationship["days_together"] in (7, 30, 365):
                days = relationship["days_together"]
                earned = self._add_milestone(milestones, f"days_{days}", f"Celebrated {days} days together.", today)
                if earned:
                    earned_titles.append(earned)
            relationship["major_milestones"] = milestones
            return relationship

        await self.relationship_store.update(update)
        return earned_titles

    @staticmethod
    def _add_milestone(milestones: list[dict[str, Any]], key: str, title: str, today: Any) -> str | None:
        if not any(milestone["key"] == key for milestone in milestones):
            milestones.append({"key": key, "title": title, "earned_on": today.isoformat()})
            return title
        return None