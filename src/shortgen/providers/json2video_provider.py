from __future__ import annotations

from pathlib import Path
import json
import time

import requests

from ..models import ContentPlan


class Json2VideoProvider:
    def __init__(
        self,
        api_key: str,
        base_url: str,
        template_id: str,
        image_model: str,
        quality: str,
        font_family: str,
        voice_model: str,
        voice_id: str,
        subtitles_model: str,
        audio_url: str,
        audio_volume: float,
    ) -> None:
        if not api_key:
            raise ValueError("JSON2VIDEO_API_KEY is required.")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.template_id = template_id
        self.image_model = image_model
        self.quality = quality
        self.font_family = font_family
        self.voice_model = voice_model
        self.voice_id = voice_id
        self.subtitles_model = subtitles_model
        self.audio_url = audio_url
        self.audio_volume = audio_volume

    def _scene_payload(self, plan: ContentPlan) -> list[dict[str, str]]:
        topic = plan.topic
        scene_prompts = [
            (
                f"{topic}. wide cinematic establishing shot. immediate visual hook. "
                "highly expressive subject. vertical 9:16. dynamic composition. no watermark."
            ),
            (
                f"{topic}. tighter reaction shot focused on the most surprising detail. "
                "strong emotion, visual escalation, dramatic contrast. vertical 9:16. no watermark."
            ),
            (
                f"{topic}. payoff aftermath shot. strongest visual consequence of the situation. "
                "memorable final frame, highly shareable, vertical 9:16. no watermark."
            ),
        ]
        voice_lines = [
            plan.hook,
            plan.audio_prompt,
            plan.cta,
        ]
        return [
            {
                "imagePrompt": image_prompt,
                "voiceOverText": voice_text,
            }
            for image_prompt, voice_text in zip(scene_prompts, voice_lines, strict=True)
        ]

    def _headers(self) -> dict[str, str]:
        return {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _raise_for_response(self, response: requests.Response, action: str) -> None:
        if response.ok:
            return
        details = ""
        try:
            details = json.dumps(response.json(), ensure_ascii=True)
        except ValueError:
            details = response.text.strip()
        raise RuntimeError(
            f"JSON2Video request failed during {action} "
            f"(HTTP {response.status_code}). Response: {details}"
        )

    def build_movie(self, plan: ContentPlan) -> dict:
        variables = {
            "scenes": self._scene_payload(plan),
            "voiceModel": self.voice_model,
            "imageModel": self.image_model,
            "subtitlesModel": self.subtitles_model,
            "fontFamily": self.font_family,
            "voiceID": self.voice_id,
        }
        if self.audio_url:
            variables["audioURL"] = self.audio_url

        return {
            "template": self.template_id,
            "comment": plan.topic,
            "variables": variables,
        }

    def _create_movie(self, movie: dict) -> str:
        response = requests.post(
            f"{self.base_url}/movies",
            headers=self._headers(),
            json=movie,
            timeout=120,
        )
        self._raise_for_response(response, "movie creation")
        payload = response.json()
        if not payload.get("success"):
            raise RuntimeError(f"JSON2Video movie creation failed: {payload}")
        project = payload.get("project")
        if not project:
            raise RuntimeError(f"JSON2Video response missing project id: {payload}")
        return project

    def _wait_for_render(self, project: str, timeout_seconds: int = 1800) -> str:
        deadline = time.time() + timeout_seconds
        delay_seconds = 30

        while time.time() < deadline:
            response = requests.get(
                f"{self.base_url}/movies",
                headers={"x-api-key": self.api_key, "Accept": "application/json"},
                params={"project": project},
                timeout=60,
            )
            self._raise_for_response(response, "movie polling")
            payload = response.json()
            movie = payload.get("movie", {})
            status = str(movie.get("status", "")).lower()

            if status == "done":
                url = movie.get("url")
                if not url:
                    raise RuntimeError(
                        f"JSON2Video render finished without a download url: {payload}"
                    )
                return url
            if status == "error":
                raise RuntimeError(f"JSON2Video render failed: {payload}")

            time.sleep(delay_seconds)
            if delay_seconds < 60:
                delay_seconds += 10

        raise TimeoutError(f"JSON2Video project {project} did not finish in time.")

    def _download_video(self, video_url: str, output_file: Path) -> Path:
        with requests.get(video_url, stream=True, timeout=300) as response:
            self._raise_for_response(response, "video download")
            with output_file.open("wb") as handle:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        handle.write(chunk)
        return output_file

    def generate(
        self,
        plan: ContentPlan,
        movie_file: Path,
        output_file: Path,
        audio_url: str | None = None,
    ) -> Path:
        if audio_url is not None:
            self.audio_url = audio_url
        movie = self.build_movie(plan)
        movie_file.write_text(json.dumps(movie, indent=2))
        project = self._create_movie(movie)
        video_url = self._wait_for_render(project)
        return self._download_video(video_url, output_file)
