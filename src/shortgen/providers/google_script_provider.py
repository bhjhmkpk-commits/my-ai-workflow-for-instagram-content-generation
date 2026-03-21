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

    def generate(self, plan: ContentPlan) -> str:
        prompt = (
            "Write one short voiceover line for a 5-second Instagram Reel.\n"
            f"Topic: {plan.topic}\n"
            f"Tone: sarcastic robotic\n"
            f"Hook: {plan.hook}\n"
            "Rules: 8 to 16 words, one sentence, no hashtags, no emojis, no quotes."
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
