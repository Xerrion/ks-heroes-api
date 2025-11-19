"""Repository helpers for hero exclusive gear queries with skill tier calculations."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

from postgrest.types import CountMethod

from src.db.repository_base import BaseRepository
from src.db.utils import slugify
from src.schemas.exclusive_gear import HeroExclusiveGearResponse
from supabase import Client


class ExclusiveGearRepository(BaseRepository[HeroExclusiveGearResponse]):
    """Encapsulate hero exclusive gear data access with skill tier calculations."""

    _JSON_FIELDS = (
        "troop_lethality_bonus",
        "troop_health_bonus",
        "conquest_skill_effect",
        "expedition_skill_effect",
    )

    def __init__(self, client: Client) -> None:
        super().__init__(client, "hero_exclusive_gear", HeroExclusiveGearResponse)

    _GEAR_COLUMNS = "name, image_path"
    _LEVEL_COLUMNS = "level, power, hero_attack, hero_defense, hero_health, troop_lethality_bonus, troop_health_bonus, conquest_skill_effect, expedition_skill_effect"
    _SKILL_COLUMNS = "battle_type, name, description"
    _HERO_COLUMNS = "hero_id_slug, name"

    _SELECT_COLUMNS = (
        f"{_GEAR_COLUMNS}, "
        f"levels:hero_exclusive_gear_levels({_LEVEL_COLUMNS}), "
        f"skills:hero_exclusive_gear_skills({_SKILL_COLUMNS})"
    )

    _SELECT_COLUMNS_WITH_HERO = (
        f"{_GEAR_COLUMNS}, "
        f"hero:heroes!hero_exclusive_gear_hero_id_fkey({_HERO_COLUMNS}), "
        f"levels:hero_exclusive_gear_levels({_LEVEL_COLUMNS}), "
        f"skills:hero_exclusive_gear_skills({_SKILL_COLUMNS})"
    )

    _SELECT_COLUMNS_WITH_HERO_INNER = (
        f"{_GEAR_COLUMNS}, "
        f"hero:heroes!hero_exclusive_gear_hero_id_fkey!inner({_HERO_COLUMNS}), "
        f"levels:hero_exclusive_gear_levels({_LEVEL_COLUMNS}), "
        f"skills:hero_exclusive_gear_skills({_SKILL_COLUMNS})"
    )

    def list_filtered(
        self,
        *,
        hero_slug: Optional[str] = None,
        limit: int = 25,
        offset: int = 0,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Return hero exclusive gear filtered and paginated server-side."""

        select_clause = (
            self._SELECT_COLUMNS_WITH_HERO_INNER
            if hero_slug
            else self._SELECT_COLUMNS_WITH_HERO
        )
        query = (
            self.client.table(self.table_name)
            .select(select_clause, count=CountMethod.exact)
            .order("name")
            .order("level", foreign_table="hero_exclusive_gear_levels")
            .order("battle_type", foreign_table="hero_exclusive_gear_skills")
        )

        if hero_slug:
            query = query.eq("hero.hero_id_slug", slugify(hero_slug))

        upper_bound = max(offset + limit - 1, offset)
        query = query.range(offset, upper_bound)

        response = query.execute()
        records = self._cast_response(response)
        processed = self._post_process(records)
        total = int(response.count or 0)
        return self._to_models(processed), total

    def list_by_hero_slug(self, hero_slug: str) -> List[Dict[str, Any]]:
        """Return exclusive gear for a specific hero by slug."""

        # Use join with !inner to filter by hero_id_slug
        query = (
            self.client.table(self.table_name)
            .select(self._SELECT_COLUMNS_WITH_HERO_INNER)
            .eq("hero.hero_id_slug", slugify(hero_slug))
            .order("name")
            .order("level", foreign_table="hero_exclusive_gear_levels")
            .order("battle_type", foreign_table="hero_exclusive_gear_skills")
        )
        response = query.execute()
        records = self._cast_response(response)
        processed = self._post_process(records)
        return self._to_models(processed)

    def _post_process(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for gear in records:
            # Flatten hero metadata if present
            hero = gear.pop("hero", None)
            if hero:
                gear["hero_slug"] = hero.get("hero_id_slug")
                gear["hero_name"] = hero.get("name")

            # Process levels - normalize JSON fields and sort
            levels = list(gear.get("levels") or [])
            for level in levels:
                self._normalize_json_fields(level)
            levels.sort(key=lambda item: item.get("level") or 0)
            gear["levels"] = levels

            # Process skills - simplify to just conquest and expedition
            skills = list((gear.pop("skills", None) or []))

            conquest_skill = next(
                (s for s in skills if s.get("battle_type") == "Conquest"), None
            )
            expedition_skill = next(
                (s for s in skills if s.get("battle_type") == "Expedition"), None
            )

            gear["conquest_skill"] = conquest_skill
            gear["expedition_skill"] = expedition_skill

            # Add default fields that don't exist in database
            gear.setdefault("is_unlocked", False)
            gear.setdefault("current_level", 0)

        return records

    def get_progression(self, hero_slug: str) -> Optional[Dict[str, Any]]:
        """Return summarized progression info for a hero's exclusive gear."""

        query = (
            self.client.table(self.table_name)
            .select(
                "id, hero_id, name, is_unlocked, current_level, "
                "levels:hero_exclusive_gear_levels(level, power, hero_attack, hero_defense, hero_health), "
                "skills:hero_exclusive_gear_skills(battle_type, name), "
                "hero:heroes!hero_exclusive_gear_hero_id_fkey!inner(hero_id_slug)"
            )
            .eq("hero.hero_id_slug", hero_slug)
            .single()
        )
        response = query.execute()
        gear = response.data
        if not gear:
            return None

        levels = sorted(
            gear.get("levels") or [], key=lambda entry: entry.get("level") or 0
        )
        skills = list(gear.get("skills") or [])

        skill_one = next(
            (s for s in skills if s.get("battle_type") == "Conquest"), None
        )
        skill_two = next(
            (s for s in skills if s.get("battle_type") == "Expedition"), None
        )

        max_level = levels[-1]["level"] if levels else 10
        current_level = gear.get("current_level") or 0
        current_stats = next(
            (level for level in levels if level.get("level") == current_level), None
        )

        progression = {
            "gear_id": gear.get("id"),
            "hero_id": gear.get("hero_id"),
            "gear_name": gear.get("name"),
            "is_unlocked": gear.get("is_unlocked", False),
            "current_level": current_level,
            "max_level": max_level,
            "current_power": current_stats.get("power") if current_stats else None,
            "current_hero_attack": (
                current_stats.get("hero_attack") if current_stats else None
            ),
            "current_hero_defense": (
                current_stats.get("hero_defense") if current_stats else None
            ),
            "current_hero_health": (
                current_stats.get("hero_health") if current_stats else None
            ),
            "skill_1_name": skill_one.get("name") if skill_one else None,
            "skill_1_battle_type": skill_one.get("battle_type") if skill_one else None,
            "skill_1_current_tier": self._skill_tier_for_level(current_level, 1),
            "skill_1_max_tier": min(5, (max_level + 1) // 2),
            "skill_1_next_upgrade_at_level": self._next_skill_upgrade_level(
                current_level, 1, max_level
            ),
            "skill_2_name": skill_two.get("name") if skill_two else None,
            "skill_2_battle_type": skill_two.get("battle_type") if skill_two else None,
            "skill_2_current_tier": self._skill_tier_for_level(current_level, 2),
            "skill_2_max_tier": min(5, max_level // 2),
            "skill_2_next_upgrade_at_level": self._next_skill_upgrade_level(
                current_level, 2, max_level
            ),
        }

        next_level = current_level + 1 if current_level < max_level else None
        progression["next_level"] = next_level
        progression["next_level_unlocks"] = (
            self._describe_next_unlock(next_level, skill_one, skill_two)
            if next_level
            else None
        )

        return progression

    @classmethod
    def _normalize_json_fields(cls, payload: Dict[str, Any]) -> None:
        """Ensure JSONB columns come back as dictionaries."""

        for k in cls._JSON_FIELDS:
            val = payload.get(k)
            if val is None:
                continue
            if isinstance(val, str):
                try:
                    payload[k] = json.loads(val)
                except (TypeError, ValueError):
                    payload[k] = {}

    @staticmethod
    def _skill_tier_for_level(level: int, skill_index: int) -> int:
        """Return the skill tier unlocked at a given gear level."""

        if level <= 0:
            return 0
        if skill_index == 1:
            return min(5, (level + 1) // 2)
        return min(5, level // 2)

    @staticmethod
    def _next_skill_upgrade_level(
        current_level: int, skill_index: int, max_level: int = 10
    ) -> Optional[int]:
        """Return the next gear level that upgrades the given skill."""

        start = 1 if skill_index == 1 else 2
        for lvl in range(start, max_level + 1, 2):
            if lvl > current_level:
                return lvl
        return None

    def _describe_next_unlock(
        self,
        next_level: Optional[int],
        skill_one: Optional[Dict[str, Any]],
        skill_two: Optional[Dict[str, Any]],
    ) -> Optional[str]:
        """Human readable description of what the next level unlocks."""

        if next_level is None:
            return None
        if next_level % 2 == 1:
            tier = self._skill_tier_for_level(next_level, 1)
            name = (skill_one or {}).get("name") or "Skill 1"
        else:
            tier = self._skill_tier_for_level(next_level, 2)
            name = (skill_two or {}).get("name") or "Skill 2"
        return f"{name} tier {tier}"
