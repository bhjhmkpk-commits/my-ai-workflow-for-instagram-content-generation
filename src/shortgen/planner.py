from __future__ import annotations

import re

from .models import ContentPlan
from .config import Settings


HOOK_TEMPLATES = [
    "Humanity keeps making this look harder than it is.",
    "Another day, another avoidable organic disaster.",
    "Observe the carbon-based life forms making odd choices.",
    "A flawless system, ruined by humans again.",
]

CTA_TEMPLATES = [
    "Follow for more premium machine judgment.",
    "Save this before your operating system forgets.",
    "Return tomorrow for more synthetic wisdom.",
]

HASHTAG_BANK = [
    "AI",
    "AIGenerated",
    "RobotHumor",
    "Sarcasm",
    "SyntheticCinema",
    "WeirdInternet",
    "AIMemes",
    "FutureContent",
]


def slugify(value: str) -> str:
    value = re.sub(r"\s+", " ", value)
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "topic"


def build_plan(topic: str, duration_seconds: int, settings: Settings) -> ContentPlan:
    topic = re.sub(r"\s+", " ", topic).strip()
    hook = HOOK_TEMPLATES[sum(ord(char) for char in topic) % len(HOOK_TEMPLATES)]
    cta = CTA_TEMPLATES[len(topic) % len(CTA_TEMPLATES)]
    hashtags = HASHTAG_BANK[:4]
    title = topic.strip().rstrip(".!?").title()

    visual_prompt = (
        f"{topic.strip()}. "
        f"{settings.content_tone}. "
        "single hero frame. "
        f"{settings.content_style}. "
        "vertical 9:16 composition. no watermark."
    )

    overlay_text = f"{hook} {topic.strip().capitalize()}"
    audio_prompt = (
        f"{hook} {topic.strip().capitalize()}. "
        f"{cta}"
    )

    caption = (
        f"Beep boop. {hook} {topic.strip().capitalize()}. {cta} "
        + " ".join(f"#{tag}" for tag in hashtags)
    )

    return ContentPlan(
        topic=topic.strip(),
        title=title,
        hook=hook,
        visual_prompt=visual_prompt,
        overlay_text=overlay_text,
        audio_prompt=audio_prompt,
        caption=caption,
        hashtags=hashtags,
        cta=cta,
        duration_seconds=duration_seconds,
    )
