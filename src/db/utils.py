"""Utility helpers shared across database repositories."""

from __future__ import annotations

import re
from typing import Any, Callable, Dict

from .storage import build_public_asset_url

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(value: str | None) -> str:
    """Lightweight slugify helper used for asset path derivation."""

    if not value:
        return ""
    return _SLUG_RE.sub("-", value.strip().lower()).strip("-")


def attach_public_asset_url(
    record: Dict[str, Any],
    *,
    path_field: str,
    url_field: str | None = None,
    bucket: str | None = None,
    default_path: str | Callable[[Dict[str, Any]], str | None] | None = None,
) -> None:
    """Add a public asset URL to a record based on a stored path.

    When ``path_field`` is empty, ``default_path`` (string or callable) can
    provide the canonical storage location before building the public URL.
    """

    path_value = record.get(path_field)
    if not path_value and default_path:
        fallback = default_path(record) if callable(default_path) else default_path
        if fallback:
            path_value = fallback
            record[path_field] = fallback

    target_field = url_field or f"{path_field}_url"
    record[target_field] = build_public_asset_url(path_value, bucket=bucket)
