"""Utility helpers shared across database repositories."""

from __future__ import annotations

from typing import Any, Dict

from .storage import build_public_asset_url


def attach_public_asset_url(
    record: Dict[str, Any],
    *,
    path_field: str,
    url_field: str | None = None,
    bucket: str | None = None,
) -> None:
    """Add a public asset URL to a record based on a stored path."""

    target_field = url_field or f"{path_field}_url"
    record[target_field] = build_public_asset_url(
        record.get(path_field), bucket=bucket
    )
