"""Repository helpers for hero exclusive gear queries."""

from __future__ import annotations

import json
from typing import Any, Dict, List, cast

from src.db.utils import attach_public_asset_url, slugify
from supabase import Client


class ExclusiveGearRepository:
    """Encapsulate hero exclusive gear data access."""

    _JSON_FIELDS = (
        "troop_lethality_bonus",
        "troop_health_bonus",
        "conquest_skill_effect",
        "expedition_skill_effect",
    )

    def __init__(self, client: Client) -> None:
        self._client = client

    _SELECT_COLUMNS = ",".join(
        [
            "id",
            "hero_id",
            "name",
            "image_path",
            "hero:heroes!hero_exclusive_gear_hero_id_fkey(id, hero_id_slug, name)",
            "levels:hero_exclusive_gear_levels(*)",
            "skills:hero_exclusive_gear_skills(*)",
        ]
    )

    def list_all(self) -> List[Dict[str, Any]]:
        """Return all hero exclusive gear with related levels and skills."""

        query = self._base_query()
        response = query.execute()
        records = cast(List[Dict[str, Any]], response.data or [])
        return self._post_process(records)

    def list_by_hero_id(self, hero_id: str) -> List[Dict[str, Any]]:
        """Return exclusive gear records for a specific hero."""

        query = self._base_query().eq("hero_id", hero_id)
        response = query.execute()
        records = cast(List[Dict[str, Any]], response.data or [])
        return self._post_process(records)

    def _base_query(self):
        return (
            self._client.table("hero_exclusive_gear")
            .select(self._SELECT_COLUMNS)
            .order("name")
            .order("level", foreign_table="hero_exclusive_gear_levels")
            .order("combat_type", foreign_table="hero_exclusive_gear_skills")
        )

    def _post_process(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for gear in records:
            gear.pop("hero", None)
            # Removed setting hero_slug and hero_name to avoid redundancy in hero-specific endpoints

            levels = list(gear.get("levels") or [])
            for level in levels:
                self._normalize_json_fields(level)
            levels.sort(key=lambda item: item.get("level") or 0)
            gear["levels"] = levels

            skills = list((gear.pop("skills", None) or []))
            for skill in skills:
                if "skill_type" not in skill:
                    skill["skill_type"] = skill.get("combat_type")
            skills.sort(
                key=lambda item: item.get("combat_type") or item.get("skill_type") or ""
            )
            skill_lookup = {"conquest": None, "expedition": None}
            for skill in skills:
                skill_type = (
                    skill.get("skill_type") or skill.get("combat_type") or ""
                ).lower()
                if skill_type in skill_lookup:
                    skill_lookup[skill_type] = skill
            gear["conquest_skill"] = skill_lookup["conquest"]
            gear["expedition_skill"] = skill_lookup["expedition"]
            gear_slug = slugify(gear.get("name"))
            default_path = (
                f"exclusive/gear/{gear_slug}.png"
                if not gear.get("image_path") and gear_slug
                else None
            )
            attach_public_asset_url(
                gear,
                path_field="image_path",
                url_field="image_url",
                default_path=default_path,
            )

        return records

    @classmethod
    def _normalize_json_fields(cls, payload: Dict[str, Any]) -> None:
        """Ensure JSONB columns come back as dictionaries."""

        for field in cls._JSON_FIELDS:
            value = payload.get(field)
            if value is None or isinstance(value, dict):
                continue
            if isinstance(value, str):
                cleaned = value.strip()
                if not cleaned:
                    payload[field] = None
                    continue
                try:
                    payload[field] = json.loads(cleaned)
                    continue
                except json.JSONDecodeError:
                    payload[field] = {"description": cleaned}
                    continue
            # fall back to wrapping any scalar value so Pydantic sees a dict
            payload[field] = {"value": value}
