from __future__ import annotations

import argparse
import json
from pathlib import Path
import random
import re
import shutil

from .config import load_settings
from .pipeline import ShortGeneratorPipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate short-form videos and publish them to Instagram Reels."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate")
    generate.add_argument("--topic", help="Topic for the Reel.")

    publish = subparsers.add_parser("publish")
    publish.add_argument("--job-dir", required=True, help="Path to an existing job directory.")

    resolve = subparsers.add_parser("resolve-instagram-id")
    resolve.add_argument("--username", required=True, help="Instagram username/handle.")

    run = subparsers.add_parser("run")
    run.add_argument("--topic", help="Topic for the Reel.")

    run_batch = subparsers.add_parser("run-batch")
    run_batch.add_argument("--count", type=int, help="Number of posts to create.")
    run_batch.add_argument("--interval-seconds", type=int, help="Delay between posts.")

    subparsers.add_parser("doctor", help="Check local configuration without generating or publishing.")

    return parser


def choose_topic(cli_topic: str | None, default_topics: list[str]) -> str:
    if cli_topic:
        return re.sub(r"\s+", " ", cli_topic).strip()
    if not default_topics:
        raise ValueError("No topic provided and DEFAULT_TOPICS is empty.")
    return re.sub(r"\s+", " ", random.choice(default_topics)).strip()


def masked_setting_report(settings) -> dict:
    required = {
        "JSON2VIDEO_API_KEY": bool(settings.json2video_api_key),
        "CLOUDINARY_URL": bool(settings.cloudinary_url),
        "INSTAGRAM_ACCESS_TOKEN": bool(settings.instagram_access_token),
        "INSTAGRAM_IG_USER_ID": bool(settings.instagram_ig_user_id),
    }
    optional = {
        "GOOGLE_API_KEY": bool(settings.google_api_key),
        "JSON2VIDEO_AUDIO_URL": bool(settings.json2video_audio_url),
        "NVIDIA_TTS_API_KEY": bool(settings.nvidia_tts_api_key),
    }
    return {
        "ready": all(required.values()) and shutil.which("ffmpeg") is not None,
        "required": required,
        "optional": optional,
        "default_topics_count": len(settings.default_topics),
        "output_dir": str(settings.output_dir),
        "topic_history_file": str(settings.topic_history_file),
        "ffmpeg_available": shutil.which("ffmpeg") is not None,
        "auto_tts_disabled": settings.shortgen_disable_tts,
        "daily_post_count": settings.daily_post_count,
        "daily_post_interval_seconds": settings.daily_post_interval_seconds,
    }


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    settings = load_settings()
    settings.output_dir.mkdir(parents=True, exist_ok=True)
    pipeline = ShortGeneratorPipeline(settings)

    if args.command == "doctor":
        print(json.dumps(masked_setting_report(settings), indent=2))
        return

    if args.command == "generate":
        topic = args.topic if args.topic else pipeline.generate_topics(1)[0]
        topic = choose_topic(topic, settings.default_topics)
        job_dir, plan = pipeline.generate(topic)
        print(json.dumps({"job_dir": str(job_dir), "plan": plan.to_dict()}, indent=2))
        return

    if args.command == "publish":
        result = pipeline.publish(Path(args.job_dir).resolve())
        print(json.dumps(result.to_dict(), indent=2))
        return

    if args.command == "resolve-instagram-id":
        ig_user_id = pipeline.publisher().resolve_ig_user_id(args.username)
        print(json.dumps({"username": args.username, "ig_user_id": ig_user_id}, indent=2))
        return

    if args.command == "run":
        topic = args.topic if args.topic else pipeline.generate_topics(1)[0]
        topic = choose_topic(topic, settings.default_topics)
        job_dir, plan, result = pipeline.run(topic)
        print(
            json.dumps(
                {
                    "job_dir": str(job_dir),
                    "plan": plan.to_dict(),
                    "publish_result": result.to_dict(),
                },
                indent=2,
            )
        )
        return

    if args.command == "run-batch":
        count = args.count or settings.daily_post_count
        interval_seconds = (
            args.interval_seconds
            if args.interval_seconds is not None
            else settings.daily_post_interval_seconds
        )
        topics = pipeline.generate_topics(count)
        results = pipeline.run_batch(topics, interval_seconds=interval_seconds)
        print(json.dumps({"results": results}, indent=2))
        return

    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    main()
