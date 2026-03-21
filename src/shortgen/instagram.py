from __future__ import annotations

from pathlib import Path
import json
import time

import requests

from .cloudinary import CloudinaryUploader
from .config import Settings
from .models import PublishResult


class InstagramPublisher:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.base_url = (
            f"https://graph.facebook.com/{self.settings.instagram_graph_version}"
        )
        self.uploader = CloudinaryUploader(self.settings.cloudinary_url)

    def upload_public_video(self, local_file: Path) -> str:
        return self.uploader.upload_video(local_file, public_id=local_file.stem)

    def create_reel_container(self, video_url: str, caption: str) -> str:
        endpoint = f"{self.base_url}/{self.settings.instagram_ig_user_id}/media"
        response = requests.post(
            endpoint,
            data={
                "media_type": "REELS",
                "video_url": video_url,
                "caption": caption,
                "share_to_feed": str(self.settings.instagram_share_to_feed).lower(),
                "access_token": self.settings.instagram_access_token,
            },
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
        return payload["id"]

    def wait_for_container(self, creation_id: str, timeout_seconds: int = 600) -> str:
        endpoint = f"{self.base_url}/{creation_id}"
        deadline = time.time() + timeout_seconds

        while time.time() < deadline:
            response = requests.get(
                endpoint,
                params={
                    "fields": "status_code,status",
                    "access_token": self.settings.instagram_access_token,
                },
                timeout=30,
            )
            response.raise_for_status()
            payload = response.json()
            status_code = payload.get("status_code") or payload.get("status") or ""

            if status_code == "FINISHED":
                return status_code
            if status_code in {"ERROR", "EXPIRED"}:
                raise RuntimeError(f"Instagram container failed with status: {payload}")

            time.sleep(10)

        raise TimeoutError("Timed out waiting for Instagram Reel processing.")

    def publish_container(self, creation_id: str) -> str:
        endpoint = f"{self.base_url}/{self.settings.instagram_ig_user_id}/media_publish"
        response = requests.post(
            endpoint,
            data={
                "creation_id": creation_id,
                "access_token": self.settings.instagram_access_token,
            },
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
        return payload["id"]

    def publish_reel(self, video_file: Path, caption: str, job_dir: Path) -> PublishResult:
        video_url = self.upload_public_video(video_file)
        creation_id = self.create_reel_container(video_url, caption)
        status_code = self.wait_for_container(creation_id)
        media_id = self.publish_container(creation_id)

        result = PublishResult(
            creation_id=creation_id,
            media_id=media_id,
            status_code=status_code,
        )
        (job_dir / "publish.json").write_text(
            json.dumps(
                {
                    **result.to_dict(),
                    "video_url": video_url,
                },
                indent=2,
            )
        )
        return result

    def resolve_ig_user_id(self, username: str) -> str:
        endpoint = f"{self.base_url}/me/accounts"
        response = requests.get(
            endpoint,
            params={
                "fields": "id,name,instagram_business_account{id,username}",
                "access_token": self.settings.instagram_access_token,
            },
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()

        for page in payload.get("data", []):
            ig_account = page.get("instagram_business_account") or {}
            if ig_account.get("username", "").lower() == username.lower():
                return ig_account["id"]

        raise RuntimeError(
            f"Could not resolve Instagram user id for username '{username}'. "
            "Check that the Facebook Page is linked to this Instagram professional account "
            "and that the token has the required permissions."
        )
