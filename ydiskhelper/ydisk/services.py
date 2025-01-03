import logging
import re
from typing import Literal, TypedDict

import requests
from django.conf import settings
from django.core.cache import cache


class FileInfo(TypedDict):
    name: str
    path: str
    type: str
    size: int
    preview: str
    mime_type: str


MediaType = Literal["audio", "book", "document", "image", "video", "compressed", "text", "unknown"]


class YandexDiskService:
    BASE_URL = "https://cloud-api.yandex.net/v1/disk/public/resources"
    PREVIEW_URL = "https://cloud-api.yandex.net/v1/disk/public/resources/preview"

    def __init__(self, public_key: str, oauth_token: str | None = None):
        self.public_key = self._normalize_public_key(public_key)
        self.oauth_token = oauth_token or getattr(settings, "YANDEX_OAUTH_TOKEN", None) or settings.YANDEX_OAUTH_CONFIG.get("OAUTH_TOKEN")

        if not self.oauth_token:
            raise ValueError("OAuth authorization required")

        if not self._check_token():
            raise ValueError("Invalid OAuth token. Re-authorization required")

    def _normalize_public_key(self, public_key: str) -> str:
        try:
            public_key = public_key.strip()

            if "disk.yandex" in public_key or "yadi.sk" in public_key:
                return public_key

            if re.match(r"^[a-zA-Z0-9_-]+$", public_key):
                return public_key

            raise ValueError(
                "Invalid link format. Supported formats:\n"
                "- https://disk.yandex.ru/d/xxx\n"
                "- https://disk.yandex.ru/i/xxx\n"
                "- https://yadi.sk/d/xxx\n"
                "- Public key"
            )

        except Exception as e:
            raise ValueError("Failed to process public link") from e

    def _get_headers(self) -> dict[str, str]:
        """Get headers for Yandex.Disk API requests"""
        headers = {"Authorization": f"OAuth {self.oauth_token}", "Accept": "application/json", "User-Agent": "YDiskHelper/1.0"}
        return headers

    def get_files(self, media_type: MediaType | None = None) -> list[FileInfo]:
        """Get list of files from public folder"""
        cache_key = f"ydisk_files_{self.public_key}_{media_type}"
        cached_files = cache.get(cache_key)

        if cached_files:
            return cached_files

        try:
            meta_params = {"public_key": self.public_key, "path": "/", "limit": 200, "offset": 0}

            meta_response = requests.get("https://cloud-api.yandex.net/v1/disk/public/resources", params=meta_params, timeout=10)

            if meta_response.status_code == 404:
                raise ValueError(
                    "Resource not found. Possible reasons:\n" "1. Invalid link\n" "2. Resource was deleted\n" "3. Access restricted by owner"
                )

            meta_response.raise_for_status()
            meta_data = meta_response.json()

            if meta_data.get("type") == "dir" and "_embedded" in meta_data:
                items = meta_data["_embedded"]["items"]
                if media_type:
                    items = [item for item in items if self._get_media_type(item.get("mime_type", "")) == media_type]
                files = [self._format_file(item) for item in items]

            else:
                files = [
                    {
                        "name": meta_data.get("name", ""),
                        "path": meta_data.get("path", "/"),
                        "type": meta_data.get("type", "file"),
                        "size": meta_data.get("size", 0),
                        "mime_type": meta_data.get("mime_type", ""),
                        "file": meta_data.get("file", ""),
                    }
                ]

            cache.set(cache_key, files, timeout=300)
            return files

        except requests.exceptions.HTTPError as e:
            logging.error(f"Critical Yandex.Disk API error: {e.response.text}", exc_info=True)
            if e.response.status_code == 401:
                raise ValueError("OAuth authorization required") from e
            raise ValueError(f"Failed to get files: {e!s}") from e

    def _format_file(self, file_data: dict) -> dict[str, str | int]:
        """Format file data for response"""
        return {
            "name": file_data.get("name", ""),
            "path": file_data.get("path", "").replace("disk:", ""),
            "type": file_data.get("type", ""),
            "size": file_data.get("size", 0),
            "preview": file_data.get("preview", ""),
            "mime_type": file_data.get("mime_type", ""),
        }

    def download_file(self, path: str) -> requests.Response:
        """Download file by path"""
        try:
            download_params = {"public_key": self.public_key, "path": path}

            download_response = requests.get("https://cloud-api.yandex.net/v1/disk/public/resources/download", params=download_params, timeout=10)

            download_response.raise_for_status()
            download_data = download_response.json()

            file_response = requests.get(download_data["href"], stream=True, timeout=30)
            file_response.raise_for_status()

            return file_response

        except requests.exceptions.RequestException as e:
            logging.error(f"Critical error downloading file {path}: {e}", exc_info=True)
            raise ValueError("Failed to download file") from e

    def _check_token(self) -> bool:
        """Check OAuth token validity"""
        try:
            response = requests.get("https://cloud-api.yandex.net/v1/disk", headers=self._get_headers(), timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def _get_media_type(self, mime_type: str) -> MediaType:
        """Determine media type from MIME type"""
        mime_map = {
            "audio": ["audio/"],
            "book": ["application/epub", "application/pdf"],
            "document": ["application/msword", "application/vnd.openxmlformats", "application/vnd.oasis"],
            "image": ["image/"],
            "video": ["video/"],
            "compressed": ["application/zip", "application/x-rar", "application/x-7z"],
            "text": ["text/"],
        }

        for media_type, mime_patterns in mime_map.items():
            if any(mime_type.startswith(pattern) for pattern in mime_patterns):
                return media_type
        return "unknown"
