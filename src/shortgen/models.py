from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ContentPlan:
    topic: str
    title: str
    hook: str
    visual_prompt: str
    overlay_text: str
    audio_prompt: str
    caption: str
    hashtags: list[str]
    cta: str
    duration_seconds: int
    aspect_ratio: str = "9:16"

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["hashtags"] = list(self.hashtags)
        return payload


@dataclass(frozen=True)
class PublishResult:
    creation_id: str
    media_id: str
    status_code: str

    def to_dict(self) -> dict:
        return asdict(self)
