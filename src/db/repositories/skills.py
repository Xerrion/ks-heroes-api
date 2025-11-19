"""Repository helpers for hero skill queries."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, cast

from src.db.repository_base import BaseRepository
from src.db.utils import slugify
from src.schemas.skills import HeroSkillResponse
from supabase import Client


class SkillsRepository(BaseRepository[HeroSkillResponse]):
    """Encapsulate hero skills data access."""

    _SELECT_WITH_HERO = "*, levels:hero_skill_levels(*), hero:heroes!hero_skills_hero_id_fkey(hero_id_slug, name)"
    _SELECT_WITH_HERO_INNER = "*, levels:hero_skill_levels(*), hero:heroes!hero_skills_hero_id_fkey!inner(hero_id_slug, name)"

    def __init__(self, client: Client) -> None:
        super().__init__(client, "hero_skills", HeroSkillResponse)

    def list_filtered(
        self,
        *,
        hero_slug: Optional[str] = None,
        skill_type: Optional[str] = None,
        battle_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[HeroSkillResponse], int]:
        """Return skills filtered and paginated server-side."""

        select_clause = (
            self._SELECT_WITH_HERO_INNER if hero_slug else self._SELECT_WITH_HERO
        )
        query = (
            self.client.table(self.table_name)
            .select(select_clause, count="exact")
            .order("name")
            .order("level", foreign_table="hero_skill_levels")
        )

        if hero_slug:
            query = query.eq("hero.hero_id_slug", slugify(hero_slug))

        if skill_type:
            query = query.eq("skill_type", skill_type)

        if battle_type:
            query = query.eq("battle_type", battle_type)

        upper_bound = max(offset + limit - 1, offset)
        query = query.range(offset, upper_bound)

        response = query.execute()
        records = self._cast_response(response)
        hydrated = self._hydrate(records)
        total = int(response.count or 0)
        return self._to_models(hydrated), total

    def list_by_hero(self, hero_id: str) -> List[HeroSkillResponse]:
        """Return skills for a specific hero by UUID."""

        query = (
            self.client.table(self.table_name)
            .select(self._SELECT_WITH_HERO)
            .eq("hero_id", hero_id)
            .order("name")
            .order("level", foreign_table="hero_skill_levels")
        )
        response = query.execute()
        records = self._cast_response(response)
        hydrated = self._hydrate(records)
        return self._to_models(hydrated)

    def list_by_hero_slug(self, hero_slug: str) -> List[HeroSkillResponse]:
        """Return skills for a specific hero by slug."""

        query = (
            self.client.table(self.table_name)
            .select(self._SELECT_WITH_HERO_INNER)
            .eq("hero.hero_id_slug", slugify(hero_slug))
            .order("name")
            .order("level", foreign_table="hero_skill_levels")
        )
        response = query.execute()
        records = self._cast_response(response)
        hydrated = self._hydrate(records)
        return self._to_models(hydrated)

    def _hydrate(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for skill in records:
            levels = list(skill.get("levels") or [])
            levels.sort(key=lambda level: level.get("level") or 0)
            skill["levels"] = levels
            skill.pop("hero", None)
        return records
