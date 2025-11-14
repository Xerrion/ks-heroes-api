"""Repository helpers for hero talent queries."""

from __future__ import annotations

from typing import Any, Dict, List, cast

from src.db.utils import attach_public_asset_url, slugify
from supabase import Client


class TalentRepository:
    """Encapsulate hero talent data access."""

    _BASE_COLUMNS = "id, hero_id, name, description, icon_path"
    _SELECT_COLUMNS = (
        f"{_BASE_COLUMNS}, hero:heroes!hero_talents_hero_id_fkey(hero_id_slug, name)"
    )

    def __init__(self, client: Client) -> None:
        self._client = client

    def list_all(self) -> List[Dict[str, Any]]:
        """Return all hero talents."""

        query = (
            self._client.table("hero_talents")
            .select(self._SELECT_COLUMNS)
            .order("name")
        )
        response = query.execute()
        records = cast(List[Dict[str, Any]], response.data or [])
        return self._hydrate(records)

    def list_by_hero(self, hero_id: str) -> List[Dict[str, Any]]:
        """Return talents for a specific hero by UUID."""

        query = (
            self._client.table("hero_talents")
            .select(self._SELECT_COLUMNS)
            .eq("hero_id", hero_id)
            .order("name")
        )
        response = query.execute()
        records = cast(List[Dict[str, Any]], response.data or [])
        return self._hydrate(records)

    def list_by_hero_slug(self, hero_slug: str) -> List[Dict[str, Any]]:
        """Return talents for a specific hero by slug."""

        # Use join with !inner to filter by hero_id_slug
        query = (
            self._client.table("hero_talents")
            .select(
                f"{self._BASE_COLUMNS}, hero:heroes!hero_talents_hero_id_fkey!inner(hero_id_slug, name)"
            )
            .eq("hero.hero_id_slug", hero_slug)
            .order("name")
        )
        response = query.execute()
        records = cast(List[Dict[str, Any]], response.data or [])
        return self._hydrate(records)

    def _hydrate(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for talent in records:
            hero = talent.pop("hero", None) or {}
            hero_slug = hero.get("hero_id_slug") or slugify(hero.get("name"))
            default_path = (
                f"talents/{hero_slug}.png"
                if hero_slug and not talent.get("icon_path")
                else None
            )
            attach_public_asset_url(
                talent,
                path_field="icon_path",
                url_field="icon_url",
                default_path=default_path,
            )
        return records
