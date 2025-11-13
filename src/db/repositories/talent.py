"""Repository helpers for hero talent queries."""

from __future__ import annotations

from typing import Any, Dict, List, cast

from src.db.utils import attach_public_asset_url
from supabase import Client


class TalentRepository:
    """Encapsulate hero talent data access."""

    _BASE_COLUMNS = "id, hero_id, name, description, icon_path"

    def __init__(self, client: Client) -> None:
        self._client = client

    def list_all(self) -> List[Dict[str, Any]]:
        """Return all hero talents."""

        query = (
            self._client.table("hero_talents").select(self._BASE_COLUMNS).order("name")
        )
        response = query.execute()
        records = cast(List[Dict[str, Any]], response.data or [])
        return self._hydrate(records)

    def list_by_hero(self, hero_id: str) -> List[Dict[str, Any]]:
        """Return talents for a specific hero."""

        query = (
            self._client.table("hero_talents")
            .select(self._BASE_COLUMNS)
            .eq("hero_id", hero_id)
            .order("name")
        )
        response = query.execute()
        records = cast(List[Dict[str, Any]], response.data or [])
        return self._hydrate(records)

    def _hydrate(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for talent in records:
            attach_public_asset_url(
                talent, path_field="icon_path", url_field="icon_url"
            )
        return records
