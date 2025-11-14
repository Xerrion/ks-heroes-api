"""Repository helpers for hero skill queries."""

from __future__ import annotations

from typing import Any, Dict, List, cast

from src.db.utils import attach_public_asset_url, slugify
from supabase import Client


class SkillsRepository:
    """Encapsulate hero skills data access."""

    def __init__(self, client: Client) -> None:
        self._client = client

    def list_all(self) -> List[Dict[str, Any]]:
        """Return all hero skills with their level details."""

        query = (
            self._client.table("hero_skills")
            .select(
                "*, levels:hero_skill_levels(*), hero:heroes!hero_skills_hero_id_fkey(hero_id_slug, name)"
            )
            .order("name")
            .order("level", foreign_table="hero_skill_levels")
        )
        response = query.execute()
        records = cast(List[Dict[str, Any]], response.data or [])
        return self._hydrate(records)

    def list_by_hero(self, hero_id: str) -> List[Dict[str, Any]]:
        """Return skills for a specific hero by UUID."""

        query = (
            self._client.table("hero_skills")
            .select(
                "*, levels:hero_skill_levels(*), hero:heroes!hero_skills_hero_id_fkey(hero_id_slug, name)"
            )
            .eq("hero_id", hero_id)
            .order("name")
            .order("level", foreign_table="hero_skill_levels")
        )
        response = query.execute()
        records = cast(List[Dict[str, Any]], response.data or [])
        return self._hydrate(records)

    def list_by_hero_slug(self, hero_slug: str) -> List[Dict[str, Any]]:
        """Return skills for a specific hero by slug."""

        # Use join with !inner to filter by hero_id_slug
        query = (
            self._client.table("hero_skills")
            .select(
                "*, levels:hero_skill_levels(*), hero:heroes!hero_skills_hero_id_fkey!inner(hero_id_slug, name)"
            )
            .eq("hero.hero_id_slug", hero_slug)
            .order("name")
            .order("level", foreign_table="hero_skill_levels")
        )
        response = query.execute()
        records = cast(List[Dict[str, Any]], response.data or [])
        return self._hydrate(records)

    def _hydrate(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for skill in records:
            levels = list(skill.get("levels") or [])
            levels.sort(key=lambda level: level.get("level") or 0)
            skill["levels"] = levels
            hero = skill.pop("hero", None) or {}
            hero_slug = hero.get("hero_id_slug") or slugify(hero.get("name"))
            skill_slug = slugify(skill.get("name"))
            default_path = (
                f"skills/{hero_slug}/{skill_slug}.png"
                if hero_slug and skill_slug and not skill.get("icon_path")
                else None
            )
            attach_public_asset_url(
                skill,
                path_field="icon_path",
                url_field="icon_url",
                default_path=default_path,
            )
        return records
