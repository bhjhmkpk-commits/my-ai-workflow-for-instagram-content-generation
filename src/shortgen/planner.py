from __future__ import annotations

import re

from .models import ContentPlan
from .config import Settings


GENERIC_HOOK_TEMPLATES = [
    "This escalated faster than anyone involved expected.",
    "Somehow this became dramatically more complicated than necessary.",
    "The situation was stable until one tiny decision ruined it.",
    "A perfectly normal moment took a wildly unnecessary turn.",
]

AI_HOOK_TEMPLATES = [
    "Humanity keeps making this look harder than it is.",
    "Another day, another avoidable organic disaster.",
    "Observe the carbon-based life forms making odd choices.",
    "A flawless system, ruined by humans again.",
]

GENERIC_CTA_TEMPLATES = [
    "Follow for more internet-grade chaos.",
    "Save this for the next unnecessary plot twist.",
    "Return tomorrow for another dramatic overreaction.",
]

AI_CTA_TEMPLATES = [
    "Follow for more premium machine judgment.",
    "Save this before your operating system forgets.",
    "Return tomorrow for more synthetic wisdom.",
]

GENERIC_HASHTAGS = [
    "TrendingReels",
    "InternetCulture",
    "MainCharacterEnergy",
    "PlotTwist",
    "RelatableChaos",
    "ViralMoments",
    "WeirdInternet",
    "DailyDrama",
]

AI_HASHTAGS = [
    "AI",
    "AIGenerated",
    "RobotHumor",
    "Sarcasm",
    "SyntheticCinema",
    "WeirdInternet",
    "AIMemes",
    "FutureContent",
]

AI_KEYWORDS = {
    "ai",
    "robot",
    "android",
    "cyborg",
    "automation",
    "machine",
    "synthetic",
    "futuristic",
    "algorithm",
    "tech",
}


def slugify(value: str) -> str:
    value = re.sub(r"\s+", " ", value)
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "topic"


def _is_ai_topic(topic: str) -> bool:
    words = set(re.findall(r"[a-z0-9]+", topic.lower()))
    return bool(words & AI_KEYWORDS)


def build_plan(topic: str, duration_seconds: int, settings: Settings) -> ContentPlan:
    topic = re.sub(r"\s+", " ", topic).strip()
    is_ai_topic = _is_ai_topic(topic)
    hook_templates = AI_HOOK_TEMPLATES if is_ai_topic else GENERIC_HOOK_TEMPLATES
    cta_templates = AI_CTA_TEMPLATES if is_ai_topic else GENERIC_CTA_TEMPLATES
    hashtag_bank = AI_HASHTAGS if is_ai_topic else GENERIC_HASHTAGS

    hook = hook_templates[sum(ord(char) for char in topic) % len(hook_templates)]
    cta = cta_templates[len(topic) % len(cta_templates)]
    hashtags = hashtag_bank[:4]
    title = topic.strip().rstrip(".!?").title()
    cleaned_topic = topic.strip().rstrip(".!?")

    if is_ai_topic:
        visual_tone = settings.content_tone
        caption_prefix = "Beep boop."
    else:
        visual_tone = "expressive, culturally aware, highly shareable"
        caption_prefix = "Current internet conditions:"

    visual_prompt = (
        f"{cleaned_topic}. "
        f"{visual_tone}. "
        "single hero frame. "
        f"{settings.content_style}. "
        "vertical 9:16 composition. no watermark."
    )

    overlay_text = f"{hook} {cleaned_topic.capitalize()}"
    audio_prompt = (
        f"{hook} {cleaned_topic.capitalize()}. "
        f"{cta}"
    )

    caption = (
        f"{caption_prefix} {hook} {cleaned_topic.capitalize()}. {cta} "
        + " ".join(f"#{tag}" for tag in hashtags)
    )

    return ContentPlan(
        topic=cleaned_topic,
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
