from __future__ import annotations

from pathlib import Path

from ..models import ContentPlan


class VideoProvider:
    def generate(
        self,
        plan: ContentPlan,
        prompt_file: Path,
        output_file: Path,
        image_file: Path | None = None,
        image_url: str | None = None,
    ) -> Path:
        raise NotImplementedError
