from __future__ import annotations

from pathlib import Path
import subprocess


def normalize_audio(
    input_file: Path,
    output_file: Path,
    duration_seconds: int,
) -> Path:
    fade_out_start = max(duration_seconds - 0.35, 0)
    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_file),
        "-af",
        (
            f"apad,atrim=0:{duration_seconds},"
            f"afade=t=out:st={fade_out_start}:d=0.35"
        ),
        "-c:a",
        "aac",
        "-b:a",
        "160k",
        "-ar",
        "48000",
        "-movflags",
        "+faststart",
        str(output_file),
    ]
    subprocess.run(command, check=True)
    return output_file


def normalize_reel(
    input_file: Path,
    output_file: Path,
    width: int,
    height: int,
    fps: int,
) -> Path:
    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_file),
        "-map",
        "0:v:0",
        "-map",
        "0:a?",
        "-vf",
        (
            f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=black,fps={fps}"
        ),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-shortest",
        "-movflags",
        "+faststart",
        str(output_file),
    ]
    subprocess.run(command, check=True)
    return output_file
