from __future__ import annotations

from pathlib import Path
import json
import re
import xml.etree.ElementTree as ET

import requests


class GoogleTrendsTopicProvider:
    def __init__(
        self,
        api_key: str,
        model: str,
        geo: str,
        history_file: Path,
    ) -> None:
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is required for topic generation.")
        self.api_key = api_key
        self.model = model
        self.geo = geo
        self.history_file = history_file

    def _fetch_trends(self, limit: int = 20) -> list[str]:
        response = requests.get(
            "https://trends.google.com/trending/rss",
            params={"geo": self.geo},
            timeout=30,
        )
        response.raise_for_status()
        root = ET.fromstring(response.text)

        titles: list[str] = []
        for item in root.findall(".//item/title"):
            if item.text:
                title = " ".join(item.text.split()).strip()
                if title:
                    titles.append(title)
            if len(titles) >= limit:
                break
        return titles

    def _load_history(self) -> list[str]:
        if not self.history_file.exists():
            return []
        return [
            line.strip()
            for line in self.history_file.read_text().splitlines()
            if line.strip()
        ]

    def _save_history(self, topics: list[str]) -> None:
        existing = self._load_history()
        merged = (existing + topics)[-200:]
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.history_file.write_text("\n".join(merged) + "\n")

    def _clean_topic(self, value: str) -> str:
        value = re.sub(r"^\s*[-*0-9.)]+\s*", "", value.strip())
        value = re.sub(r"\s+", " ", value)
        return value[:120].strip()

    def generate_topics(self, count: int) -> list[str]:
        trends = self._fetch_trends()
        history = self._load_history()[-30:]

        prompt = (
            "Create short Instagram Reel topic ideas for an AI meme page.\n"
            "Use the trending search list as inspiration, but transform them into absurd, "
            "sarcastic, robotic, AI-themed concepts.\n"
            f"Need exactly {count} topics.\n"
            "Rules: one line per topic, 4 to 12 words, no numbering, no hashtags, "
            "no emojis, no quotes.\n"
            "Avoid repeating or being too similar to the recent topic history.\n"
            f"Trending searches ({self.geo}): {', '.join(trends)}\n"
            f"Recent topic history: {', '.join(history) if history else 'none'}"
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
        response.raise_for_status()
        payload = response.json()
        candidates = payload.get("candidates") or []
        if not candidates:
            raise RuntimeError(f"Google topic generation returned no candidates: {payload}")

        parts = candidates[0].get("content", {}).get("parts", [])
        text = "".join(part.get("text", "") for part in parts)
        topics = []
        for line in text.splitlines():
            cleaned = self._clean_topic(line)
            if cleaned:
                topics.append(cleaned)
            if len(topics) >= count:
                break

        if len(topics) < count:
            raise RuntimeError(
                f"Google topic generation returned too few topics: {topics!r}"
            )

        self._save_history(topics)
        return topics
