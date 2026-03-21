from __future__ import annotations

from pathlib import Path
from dataclasses import replace
import json
from datetime import datetime
import time

from .config import Settings
from .cloudinary import CloudinaryUploader
from .instagram import InstagramPublisher
from .media import normalize_reel
from .models import ContentPlan, PublishResult
from .planner import build_plan, slugify
from .providers.google_script_provider import GoogleScriptProvider
from .providers.google_trends_topic_provider import GoogleTrendsTopicProvider
from .providers.nvidia_tts_provider import NvidiaTtsProvider
from .providers.json2video_provider import Json2VideoProvider


class ShortGeneratorPipeline:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def publisher(self) -> InstagramPublisher:
        return InstagramPublisher(self.settings)

    def topic_provider(self) -> GoogleTrendsTopicProvider | None:
        if not self.settings.google_api_key:
            return None
        return GoogleTrendsTopicProvider(
            api_key=self.settings.google_api_key,
            model=self.settings.google_topic_model,
            geo=self.settings.google_trends_geo,
            history_file=self.settings.topic_history_file,
        )

    def create_job_dir(self, topic: str) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        slug = slugify(topic)[:60]
        job_dir = self.settings.output_dir / f"{timestamp}-{slug}"
        job_dir.mkdir(parents=True, exist_ok=False)
        return job_dir

    def generate(self, topic: str) -> tuple[Path, ContentPlan]:
        job_dir = self.create_job_dir(topic)
        plan = build_plan(topic, self.settings.reel_duration_seconds, self.settings)
        script_provider = None
        if self.settings.google_api_key:
            script_provider = GoogleScriptProvider(
                api_key=self.settings.google_api_key,
                model=self.settings.google_script_model,
            )
        video_provider = Json2VideoProvider(
            api_key=self.settings.json2video_api_key,
            base_url=self.settings.json2video_base_url,
            image_model=self.settings.json2video_image_model,
            quality=self.settings.json2video_quality,
            font_family=self.settings.json2video_font_family,
            audio_url=self.settings.json2video_audio_url,
            audio_volume=self.settings.json2video_audio_volume,
        )
        uploader = CloudinaryUploader(self.settings.cloudinary_url)
        tts_provider = None
        if self.settings.nvidia_tts_script_path and not self.settings.shortgen_disable_tts:
            tts_provider = NvidiaTtsProvider(
                script_path=self.settings.nvidia_tts_script_path,
                server=self.settings.nvidia_tts_server,
                use_ssl=self.settings.nvidia_tts_use_ssl,
                function_id=self.settings.nvidia_tts_function_id,
                api_key=self.settings.nvidia_tts_api_key,
                language_code=self.settings.nvidia_tts_language_code,
                voice=self.settings.nvidia_tts_voice,
            )

        movie_file = job_dir / "movie.json"
        audio_file = job_dir / "audio.wav"
        raw_video = job_dir / "raw.mp4"
        reel_video = job_dir / "reel.mp4"
        plan_file = job_dir / "plan.json"

        if script_provider:
            generated_audio_prompt = script_provider.generate(plan)
            plan = replace(plan, audio_prompt=generated_audio_prompt)

        plan_file.write_text(json.dumps(plan.to_dict(), indent=2))

        audio_url = self.settings.json2video_audio_url
        if tts_provider:
            try:
                tts_provider.generate(plan, output_file=audio_file)
                audio_url = uploader.upload_raw(
                    audio_file,
                    public_id=f"{job_dir.name}-audio",
                )
            except Exception as exc:
                print(f"TTS skipped: {exc}")

        video_provider.generate(
            plan,
            movie_file=movie_file,
            audio_url=audio_url,
            output_file=raw_video,
        )
        normalize_reel(
            raw_video,
            reel_video,
            width=self.settings.reel_width,
            height=self.settings.reel_height,
            fps=self.settings.reel_fps,
        )

        return job_dir, plan

    def publish(self, job_dir: Path) -> PublishResult:
        plan = ContentPlan(**json.loads((job_dir / "plan.json").read_text()))
        reel_video = job_dir / "reel.mp4"
        return self.publisher().publish_reel(reel_video, plan.caption, job_dir)

    def run(self, topic: str) -> tuple[Path, ContentPlan, PublishResult]:
        job_dir, plan = self.generate(topic)
        result = self.publish(job_dir)
        return job_dir, plan, result

    def run_batch(
        self,
        topics: list[str],
        interval_seconds: int,
    ) -> list[dict]:
        results = []
        for index, topic in enumerate(topics):
            job_dir, plan, result = self.run(topic)
            results.append(
                {
                    "job_dir": str(job_dir),
                    "plan": plan.to_dict(),
                    "publish_result": result.to_dict(),
                }
            )
            if index < len(topics) - 1 and interval_seconds > 0:
                time.sleep(interval_seconds)
        return results

    def generate_topics(self, count: int) -> list[str]:
        provider = self.topic_provider()
        if provider:
            return provider.generate_topics(count)
        if not self.settings.default_topics:
            raise ValueError("No default topics configured.")
        return self.settings.default_topics[:count]
