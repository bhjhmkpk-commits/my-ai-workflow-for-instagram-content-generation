from __future__ import annotations

from pathlib import Path
import os
import subprocess

from ..models import ContentPlan


class NvidiaTtsProvider:
    def __init__(
        self,
        script_path: str,
        server: str,
        use_ssl: bool,
        function_id: str,
        api_key: str,
        language_code: str,
        voice: str,
    ) -> None:
        if not script_path or not api_key or not function_id:
            raise ValueError(
                "NVIDIA_TTS_SCRIPT_PATH, NVIDIA_TTS_API_KEY, and "
                "NVIDIA_TTS_FUNCTION_ID are required."
            )
        self.script_path = script_path
        self.server = server
        self.use_ssl = use_ssl
        self.function_id = function_id
        self.api_key = api_key
        self.language_code = language_code
        self.voice = voice

    def generate(self, plan: ContentPlan, output_file: Path) -> Path:
        if not os.path.exists(self.script_path):
            raise FileNotFoundError(
                f"NVIDIA TTS script not found at {self.script_path}"
            )

        command = [
            "python",
            self.script_path,
            "--server",
            self.server,
        ]
        if self.use_ssl:
            command.append("--use-ssl")
        command.extend(
            [
                "--metadata",
                "function-id",
                self.function_id,
                "--metadata",
                "authorization",
                f"Bearer {self.api_key}",
                "--language-code",
                self.language_code,
                "--text",
                plan.audio_prompt,
                "--voice",
                self.voice,
                "--output",
                str(output_file),
            ]
        )

        subprocess.run(command, check=True)
        if not output_file.exists():
            raise FileNotFoundError(
                f"NVIDIA TTS command completed but did not create {output_file}"
            )
        return output_file
