"""Local, predictable emotion detection for Luna."""

from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Emotion:
    name: str
    intensity: float
    confidence: float


class EmotionEngine:
    """Detects the general emotional tone of a message."""

    EMOTION_PATTERNS = {
        "happy": (
            r"\bhappy\b",
            r"\bexcited\b",
            r"\bamazing\b",
            r"\bgreat\b",
            r"\bawesome\b",
            r"\bjoy\b",
            r"\blove it\b",
            r"\byay\b",
            r"\blets go\b",
        ),
        "sad": (
            r"\bsad\b",
            r"\bsadness\b",
            r"\bupset\b",
            r"\bdepressed\b",
            r"\blonely\b",
            r"\bcrying\b",
            r"\bmiss\b",
            r"\bhurt\b",
        ),
        "angry": (
            r"\bangry\b",
            r"\bmad\b",
            r"\bfurious\b",
            r"\bhate\b",
            r"\bpissed\b",
            r"\bannoyed\b",
            r"\birritated\b",
        ),
        "stressed": (
            r"\bstressed\b",
            r"\bstress\b",
            r"\bworried\b",
            r"\banxious\b",
            r"\boverwhelmed\b",
            r"\bpressure\b",
            r"\bnervous\b",
        ),
        "confused": (
            r"\bconfused\b",
            r"\bconfusing\b",
            r"\bdon't understand\b",
            r"\bwhat do i do\b",
            r"\bwhy is\b",
            r"\bhow does\b",
        ),
        "playful": (
            r"\blol\b",
            r"\blmao\b",
            r"\bhaha\b",
            r"\b😂\b",
            r"\b🤣\b",
            r"\bjk\b",
            r"\bjust kidding\b",
        ),
    }

    def detect(self, message: str) -> Emotion:
        """Detect the strongest emotional signal in a message."""

        text = " ".join(message.casefold().split())

        if not text:
            return Emotion(
                name="neutral",
                intensity=0.0,
                confidence=1.0,
            )

        scores: dict[str, int] = {}

        for emotion, patterns in self.EMOTION_PATTERNS.items():
            score = 0

            for pattern in patterns:
                if re.search(pattern, text):
                    score += 1

            if score:
                scores[emotion] = score

        if not scores:
            return Emotion(
                name="neutral",
                intensity=0.0,
                confidence=0.8,
            )

        emotion_name = max(
            scores,
            key=scores.get,
        )

        matches = scores[emotion_name]

        intensity = min(
            1.0,
            0.35 + (matches * 0.2),
        )

        confidence = min(
            1.0,
            0.65 + (matches * 0.1),
        )

        # Strong punctuation can indicate higher intensity.
        if "!!" in text:
            intensity = min(
                1.0,
                intensity + 0.15,
            )

        return Emotion(
            name=emotion_name,
            intensity=round(intensity, 2),
            confidence=round(confidence, 2),
        )

    def process(self, message: str) -> Emotion:
        """Main entry point for emotion detection."""

        return self.detect(message)