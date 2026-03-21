from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse
import hashlib
import json
import time

import requests


@dataclass(frozen=True)
class CloudinaryConfig:
    cloud_name: str
    api_key: str
    api_secret: str


def parse_cloudinary_url(cloudinary_url: str) -> CloudinaryConfig:
    parsed = urlparse(cloudinary_url)
    if parsed.scheme != "cloudinary":
        raise ValueError("CLOUDINARY_URL must use the cloudinary:// scheme.")
    if not parsed.username or not parsed.password or not parsed.hostname:
        raise ValueError("CLOUDINARY_URL is missing cloud name, API key, or API secret.")
    return CloudinaryConfig(
        cloud_name=parsed.hostname,
        api_key=parsed.username,
        api_secret=parsed.password,
    )


class CloudinaryUploader:
    def __init__(self, cloudinary_url: str) -> None:
        if not cloudinary_url:
            raise ValueError("CLOUDINARY_URL is required for publishing.")
        self.config = parse_cloudinary_url(cloudinary_url)

    def upload_video(self, local_file: Path, public_id: str) -> str:
        return self._upload_media(local_file, public_id=public_id, resource_type="video")

    def upload_image(self, local_file: Path, public_id: str) -> str:
        return self._upload_media(local_file, public_id=public_id, resource_type="image")

    def upload_raw(self, local_file: Path, public_id: str) -> str:
        return self._upload_media(local_file, public_id=public_id, resource_type="raw")

    def _upload_media(
        self,
        local_file: Path,
        public_id: str,
        resource_type: str,
    ) -> str:
        timestamp = int(time.time())
        signature_base = f"public_id={public_id}&timestamp={timestamp}{self.config.api_secret}"
        signature = hashlib.sha1(signature_base.encode("utf-8")).hexdigest()

        endpoint = (
            f"https://api.cloudinary.com/v1_1/{self.config.cloud_name}/"
            f"{resource_type}/upload"
        )
        with local_file.open("rb") as handle:
            response = requests.post(
                endpoint,
                data={
                    "api_key": self.config.api_key,
                    "timestamp": timestamp,
                    "public_id": public_id,
                    "resource_type": resource_type,
                    "signature": signature,
                },
                files={"file": handle},
                timeout=300,
            )
        if not response.ok:
            details = ""
            try:
                details = json.dumps(response.json(), ensure_ascii=True)
            except ValueError:
                details = response.text.strip()
            raise RuntimeError(
                f"Cloudinary upload failed for {resource_type} "
                f"(HTTP {response.status_code}). Response: {details}"
            )
        payload = response.json()
        return payload["secure_url"]
