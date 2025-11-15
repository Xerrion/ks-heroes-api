"""Supabase Storage helpers for KingShot Heroes."""

from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from mimetypes import guess_type
from pathlib import Path
from typing import Iterable

from src.settings import get_supabase_settings
from src.db.supabase_client import get_supabase_client

DEFAULT_BUCKET = "assets"
_BUCKET_ENV_VAR = "SUPABASE_STORAGE_BUCKET"


def get_storage_bucket() -> str:
    """Return the configured storage bucket name (defaulting when unset)."""

    return os.getenv(_BUCKET_ENV_VAR, DEFAULT_BUCKET)


@lru_cache(maxsize=1)
def _public_base_url() -> str | None:
    try:
        settings = get_supabase_settings()
    except RuntimeError:
        return None
    return f"{str(settings.url).rstrip('/')}/storage/v1/object/public"


def build_public_asset_url(
    path: str | None, *, bucket: str | None = None
) -> str | None:
    """Build the public URL for an asset stored in Supabase Storage."""

    if not path:
        return None

    base_url = _public_base_url()
    if base_url is None:
        return None

    bucket_name = bucket or get_storage_bucket()
    normalized = path.lstrip("/")
    return f"{base_url}/{bucket_name}/{normalized}"


def ensure_bucket_exists(*, bucket: str | None = None, public: bool = True) -> None:
    """Ensure the target bucket exists (creates it when missing)."""

    bucket_name = bucket or get_storage_bucket()
    client = get_supabase_client()
    existing = {entry.name for entry in client.storage.list_buckets()}
    if bucket_name in existing:
        if public:
            # Make sure the bucket stays public if requested
            client.storage.update_bucket(bucket_name, {"public": True})
        return

    client.storage.create_bucket(bucket_name, options={"public": public})


def upload_file(
    local_path: Path,
    storage_path: str,
    *,
    bucket: str | None = None,
    content_type: str | None = None,
    cache_control: int = 3600,
    upsert: bool = True,
) -> str:
    """Upload a file to Supabase Storage and return the public URL."""

    bucket_name = bucket or get_storage_bucket()
    with open(local_path, "rb") as f:
        inferred_type = (
            content_type
            or guess_type(local_path.as_posix())[0]
            or "application/octet-stream"
        )

        file_options: dict[str, str] = {
            "content-type": inferred_type,
        }
        if cache_control is not None:
            file_options["cache-control"] = str(cache_control)
        if upsert:
            file_options["upsert"] = "true"

        client = get_supabase_client()
        response = client.storage.from_(bucket_name).upload(
            storage_path,
            f,
            file_options=file_options,
        )

    if getattr(
        response, "error", None
    ):  # pragma: no cover - depends on client internals
        raise RuntimeError(
            f"Failed to upload {local_path} to {bucket_name}/{storage_path}: {response.error}"
        )

    public_url = build_public_asset_url(storage_path, bucket=bucket_name)
    if public_url is None:  # pragma: no cover - depends on environment configuration
        raise RuntimeError(
            "Supabase configuration missing: cannot build asset URL after upload"
        )

    return public_url


def upload_directory(
    directory: Path,
    *,
    bucket: str | None = None,
    prefix: str = "",
    patterns: Iterable[str] | None = None,
    cache_control: int = 3600,
    upsert: bool = True,
) -> list[str]:
    """Upload all matching files within a directory.

    Returns a list of public URLs for the uploaded assets.
    """

    directory = Path(directory)
    if not directory.exists() or not directory.is_dir():
        raise FileNotFoundError(
            f"Directory {directory} does not exist or is not a directory"
        )

    ensure_bucket_exists(bucket=bucket)

    patterns = tuple(patterns or ("*.png", "*.jpg", "*.jpeg", "*.webp", "*.svg"))
    files_to_upload = []

    for pattern in patterns:
        for file_path in directory.rglob(pattern):
            if not file_path.is_file():
                continue

            relative = file_path.relative_to(directory)
            storage_path = Path(prefix) / relative if prefix else relative
            storage_key = storage_path.as_posix()
            files_to_upload.append((file_path, storage_key))

    uploaded_urls = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(
                upload_file,
                file_path,
                storage_key,
                bucket=bucket,
                cache_control=cache_control,
                upsert=upsert,
            )
            for file_path, storage_key in files_to_upload
        ]
        for future in as_completed(futures):
            uploaded_urls.append(future.result())

    return uploaded_urls
