from __future__ import annotations

import json

import requests

from ..models import ContentPlan


class GoogleScriptProvider:
    def __init__(self, api_key: str, model: str) -> None:
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is required for script generation.")
        self.api_key = api_key
        self.model = model

    def _raise_for_response(self, response: requests.Response) -> None:
        if response.ok:
            return
        details = ""
        try:
            details = json.dumps(response.json(), ensure_ascii=True)
        except ValueError:
            details = response.text.strip()
        raise RuntimeError(
            f"Google script generation failed "
            f"(HTTP {response.status_code}). Response: {details}"
        )

    def _tone_for_topic(self, plan: ContentPlan) -> str:
        caption_text = plan.caption.lower()
        if "beep boop" in caption_text or any(
            token in plan.topic.lower()
            for token in ("ai", "robot", "android", "cyborg", "machine", "automation")
        ):
            return "meme-y, sharp, sarcastic, slightly robotic but still human-sounding"
        return "meme-y, silly, human, culturally aware, funny, and specific to the topic"

    def generate(self, plan: ContentPlan) -> str:
        prompt = (
            "Write one short voiceover line for a 5-second Instagram Reel.\n"
            f"Topic: {plan.topic}\n"
            f"Tone: {self._tone_for_topic(plan)}\n"
            f"Hook: {plan.hook}\n"
            "Rules: 6 to 14 words, one sentence, no hashtags, no emojis, no quotes.\n"
            "Make it sound like a human meme voiceover, not formal narration.\n"
            "It can use casual filler or reaction sounds like wait, bro, nah, arre, uff, or oh no when natural.\n"
            "Use the language or mixed-language internet phrasing that best fits the topic; do not force plain English.\n"
            "Make it clearly about the topic itself, not a generic robot narrator.\n"
            "Do not mention AI, robots, systems, or machines unless the topic is actually about that."
        )
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent",
            headers={
                "x-goog-api-key": self.api_key,
                "Content-Type": "application/json",
            },
            json={
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt,
                            }
                        ]
                    }
                ]
            },
            timeout=60,
        )
        self._raise_for_response(response)
        payload = response.json()
        candidates = payload.get("candidates") or []
        if not candidates:
            raise RuntimeError(f"Google script generation returned no candidates: {payload}")
        parts = candidates[0].get("content", {}).get("parts", [])
        text = "".join(part.get("text", "") for part in parts).strip()
        if not text:
            raise RuntimeError(f"Google script generation returned empty text: {payload}")
        return " ".join(text.split())
