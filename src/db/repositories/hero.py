"""Repository helpers for hero queries."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, cast

from src.db.utils import attach_public_asset_url, slugify
from supabase import Client


class HeroRepository:
    """Encapsulate hero data access."""

    _BASE_COLUMNS = "id, hero_id_slug, name, rarity, generation, class, image_path"

    def __init__(self, client: Client) -> None:
        self._client = client

    @staticmethod
    def _default_image_path(hero: Dict[str, Any]) -> str | None:
        hero_slug = hero.get("hero_id_slug") or slugify(hero.get("name"))
        return f"heroes/{hero_slug}.png" if hero_slug else None

    def list_all(self) -> List[Dict[str, Any]]:
        """Return all heroes with their basic attributes."""

        query = self._client.table("heroes").select(self._BASE_COLUMNS).order("name")
        response = query.execute()
        records = cast(List[Dict[str, Any]], response.data or [])
        for hero in records:
            attach_public_asset_url(
                hero,
                path_field="image_path",
                url_field="image_url",
                default_path=self._default_image_path(hero),
            )
        return records

    def get_by_slug(self, hero_slug: str) -> Optional[Dict[str, Any]]:
        """Return a single hero by slug or None when it does not exist."""

        query = (
            self._client.table("heroes")
            .select(self._BASE_COLUMNS)
            .eq("hero_id_slug", hero_slug)
            .single()
        )
        response = query.execute()
        record = cast(Optional[Dict[str, Any]], response.data)
        if record:
            attach_public_asset_url(
                record,
                path_field="image_path",
                url_field="image_url",
                default_path=self._default_image_path(record),
            )
        return record
