from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv() -> None:
        env_path = Path(".env")
        if not env_path.exists():
            return
        for raw_line in env_path.read_text().splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


@dataclass(frozen=True)
class Settings:
    output_dir: Path
    default_topics: list[str]
    json2video_api_key: str
    json2video_base_url: str
    json2video_template_id: str
    json2video_image_model: str
    json2video_quality: str
    json2video_font_family: str
    json2video_voice_model: str
    json2video_voice_id: str
    json2video_subtitles_model: str
    json2video_audio_url: str
    json2video_audio_volume: float
    google_api_key: str
    google_script_model: str
    google_trends_geo: str
    google_topic_model: str
    topic_history_file: Path
    nvidia_tts_script_path: str
    nvidia_tts_server: str
    nvidia_tts_use_ssl: bool
    nvidia_tts_function_id: str
    nvidia_tts_api_key: str
    nvidia_tts_language_code: str
    nvidia_tts_voice: str
    shortgen_disable_tts: bool
    daily_post_count: int
    daily_post_interval_seconds: int
    cloudinary_url: str
    instagram_graph_version: str
    instagram_access_token: str
    instagram_ig_user_id: str
    instagram_share_to_feed: bool
    reel_duration_seconds: int
    reel_width: int
    reel_height: int
    reel_fps: int
    content_tone: str
    content_style: str


def _parse_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def load_settings() -> Settings:
    load_dotenv()

    topics = [
        topic.strip()
        for topic in os.getenv("DEFAULT_TOPICS", "").split(",")
        if topic.strip()
    ]

    return Settings(
        output_dir=Path(os.getenv("SHORTGEN_OUTPUT_DIR", "./output")).resolve(),
        default_topics=topics,
        json2video_api_key=os.getenv("JSON2VIDEO_API_KEY", "").strip(),
        json2video_base_url=os.getenv(
            "JSON2VIDEO_BASE_URL",
            "https://api.json2video.com/v2",
        ).strip(),
        json2video_template_id=os.getenv(
            "JSON2VIDEO_TEMPLATE_ID",
            "hdpPVeEfgB3G9RH3W8dL",
        ).strip(),
        json2video_image_model=os.getenv(
            "JSON2VIDEO_IMAGE_MODEL",
            "freepik-classic",
        ).strip(),
        json2video_quality=os.getenv("JSON2VIDEO_QUALITY", "medium").strip(),
        json2video_font_family=os.getenv("JSON2VIDEO_FONT_FAMILY", "Roboto").strip(),
        json2video_voice_model=os.getenv("JSON2VIDEO_VOICE_MODEL", "azure").strip(),
        json2video_voice_id=os.getenv(
            "JSON2VIDEO_VOICE_ID",
            "en-US-EmmaMultilingualNeural",
        ).strip(),
        json2video_subtitles_model=os.getenv(
            "JSON2VIDEO_SUBTITLES_MODEL",
            "default",
        ).strip(),
        json2video_audio_url=os.getenv("JSON2VIDEO_AUDIO_URL", "").strip(),
        json2video_audio_volume=float(os.getenv("JSON2VIDEO_AUDIO_VOLUME", "0.22")),
        google_api_key=os.getenv("GOOGLE_API_KEY", "").strip(),
        google_script_model=os.getenv("GOOGLE_SCRIPT_MODEL", "gemini-2.5-flash").strip(),
        google_trends_geo=os.getenv("GOOGLE_TRENDS_GEO", "US").strip(),
        google_topic_model=os.getenv("GOOGLE_TOPIC_MODEL", "gemini-2.5-flash").strip(),
        topic_history_file=Path(
            os.getenv("TOPIC_HISTORY_FILE", "./output/topic-history.txt")
        ).resolve(),
        nvidia_tts_script_path=os.getenv("NVIDIA_TTS_SCRIPT_PATH", "").strip(),
        nvidia_tts_server=os.getenv("NVIDIA_TTS_SERVER", "grpc.nvcf.nvidia.com:443").strip(),
        nvidia_tts_use_ssl=_parse_bool(os.getenv("NVIDIA_TTS_USE_SSL", "true"), default=True),
        nvidia_tts_function_id=os.getenv(
            "NVIDIA_TTS_FUNCTION_ID",
            "877104f7-e885-42b9-8de8-f6e4c6303969",
        ).strip(),
        nvidia_tts_api_key=os.getenv("NVIDIA_TTS_API_KEY", "").strip(),
        nvidia_tts_language_code=os.getenv("NVIDIA_TTS_LANGUAGE_CODE", "en-US").strip(),
        nvidia_tts_voice=os.getenv(
            "NVIDIA_TTS_VOICE",
            "Magpie-Multilingual.EN-US.Aria",
        ).strip(),
        shortgen_disable_tts=_parse_bool(
            os.getenv("SHORTGEN_DISABLE_TTS", "false"),
            default=False,
        ),
        daily_post_count=int(os.getenv("DAILY_POST_COUNT", "2")),
        daily_post_interval_seconds=int(
            os.getenv("DAILY_POST_INTERVAL_SECONDS", "43200")
        ),
        cloudinary_url=os.getenv("CLOUDINARY_URL", "").strip(),
        instagram_graph_version=os.getenv("INSTAGRAM_GRAPH_VERSION", "v23.0").strip(),
        instagram_access_token=os.getenv("INSTAGRAM_ACCESS_TOKEN", "").strip(),
        instagram_ig_user_id=os.getenv("INSTAGRAM_IG_USER_ID", "").strip(),
        instagram_share_to_feed=_parse_bool(
            os.getenv("INSTAGRAM_SHARE_TO_FEED", "true"),
            default=True,
        ),
        reel_duration_seconds=int(os.getenv("REEL_DURATION_SECONDS", "5")),
        reel_width=int(os.getenv("REEL_WIDTH", "1080")),
        reel_height=int(os.getenv("REEL_HEIGHT", "1920")),
        reel_fps=int(os.getenv("REEL_FPS", "30")),
        content_tone=os.getenv("CONTENT_TONE", "sarcastic robotic").strip(),
        content_style=os.getenv(
            "CONTENT_STYLE",
            "absurd ai-generated scenes, cinematic, vertical, meme-friendly",
        ).strip(),
    )
