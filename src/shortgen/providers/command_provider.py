from __future__ import annotations

from pathlib import Path
import shlex
import subprocess

from ..models import ContentPlan
from .base import VideoProvider


class CommandVideoProvider(VideoProvider):
    def __init__(self, command_template: str) -> None:
        if not command_template:
            raise ValueError("VIDEO_GENERATOR_COMMAND is required.")
        self.command_template = command_template

    def generate(
        self,
        plan: ContentPlan,
        prompt_file: Path,
        output_file: Path,
        image_file: Path | None = None,
        image_url: str | None = None,
    ) -> Path:
        command = self.command_template.format(
            prompt_file=shlex.quote(str(prompt_file)),
            image_file=shlex.quote(str(image_file)) if image_file else "",
            image_url=shlex.quote(str(image_url)) if image_url else "",
            output_file=shlex.quote(str(output_file)),
            duration_seconds=plan.duration_seconds,
            aspect_ratio=plan.aspect_ratio,
            title=shlex.quote(plan.title),
        )

        subprocess.run(command, shell=True, check=True)

        if not output_file.exists():
            raise FileNotFoundError(
                f"Video generator command completed but did not create {output_file}"
            )
        return output_file
