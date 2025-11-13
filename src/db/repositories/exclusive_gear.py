"""Repository helpers for hero exclusive gear queries with skill tier calculations."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, cast

from supabase import Client

from src.db.utils import attach_public_asset_url


class ExclusiveGearRepository:
    """Encapsulate hero exclusive gear data access with skill tier calculations."""

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
            "is_unlocked",
            "current_level",
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
    
    def get_by_hero_id(self, hero_id: str) -> Optional[Dict[str, Any]]:
        """
        Get exclusive gear for a specific hero with complete progression info.
        
        Returns gear with:
        - All level stats (1-10)
        - Skills with calculated tiers at each level
        - Progression metadata
        """
        query = self._base_query().eq("hero_id", hero_id).maybe_single()
        response = query.execute()
        
        if not response.data:
            return None
        
        gear = response.data
        records = [gear] if gear else []
        processed = self._post_process(records, include_skill_tiers=True)
        return processed[0] if processed else None
    
    def get_progression(self, hero_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed progression info for a hero's exclusive gear.
        Shows current state and next upgrade information.
        """
        gear = self.get_by_hero_id(hero_id)
        if not gear:
            return None
        
        current_level = gear.get("current_level", 0)
        levels = gear.get("levels", [])
        skills = gear.get("skills", [])
        
        # Find current level stats
        current_stats = next(
            (lvl for lvl in levels if lvl["level"] == current_level),
            None
        )
        
        # Get skills
        skill_1 = skills[0] if len(skills) > 0 else None
        skill_2 = skills[1] if len(skills) > 1 else None
        
        # Calculate current tiers
        skill_1_tier = self._calculate_skill_tier(current_level, 1)
        skill_2_tier = self._calculate_skill_tier(current_level, 2)
        
        # Calculate next upgrade info
        next_level = current_level + 1 if current_level < 10 else None
        next_upgrade = None
        
        if next_level:
            next_skill_1_tier = self._calculate_skill_tier(next_level, 1)
            next_skill_2_tier = self._calculate_skill_tier(next_level, 2)
            
            if next_skill_1_tier > skill_1_tier:
                skill_name = skill_1["name"] if skill_1 else "Skill 1"
                next_upgrade = f"{skill_name} → Tier {next_skill_1_tier}"
            elif next_skill_2_tier > skill_2_tier:
                skill_name = skill_2["name"] if skill_2 else "Skill 2"
                next_upgrade = f"{skill_name} → Tier {next_skill_2_tier}"
        
        return {
            "gear_id": gear["id"],
            "hero_id": gear["hero_id"],
            "gear_name": gear["name"],
            "is_unlocked": gear.get("is_unlocked", False),
            "current_level": current_level,
            "max_level": 10,
            "current_power": current_stats["power"] if current_stats else None,
            "current_hero_attack": current_stats["hero_attack"] if current_stats else None,
            "current_hero_defense": current_stats["hero_defense"] if current_stats else None,
            "current_hero_health": current_stats["hero_health"] if current_stats else None,
            "skill_1_name": skill_1["name"] if skill_1 else None,
            "skill_1_combat_type": skill_1["combat_type"] if skill_1 else None,
            "skill_1_current_tier": skill_1_tier,
            "skill_1_max_tier": 5,
            "skill_1_next_upgrade_at_level": self._next_skill_upgrade_level(current_level, 1),
            "skill_2_name": skill_2["name"] if skill_2 else None,
            "skill_2_combat_type": skill_2["combat_type"] if skill_2 else None,
            "skill_2_current_tier": skill_2_tier,
            "skill_2_max_tier": 5,
            "skill_2_next_upgrade_at_level": self._next_skill_upgrade_level(current_level, 2),
            "next_level": next_level,
            "next_level_unlocks": next_upgrade,
        }

    def _base_query(self):
        return (
            self._client.table("hero_exclusive_gear")
            .select(self._SELECT_COLUMNS)
            .order("name")
            .order("level", foreign_table="hero_exclusive_gear_levels")
            .order("combat_type", foreign_table="hero_exclusive_gear_skills")
        )

    def _post_process(self, records: List[Dict[str, Any]], include_skill_tiers: bool = False) -> List[Dict[str, Any]]:
        for gear in records:
            levels = list(gear.get("levels") or [])
            for level in levels:
                self._normalize_json_fields(level)
                if include_skill_tiers:
                    level["skill_1_tier"] = self._calculate_skill_tier(level["level"], 1)
                    level["skill_2_tier"] = self._calculate_skill_tier(level["level"], 2)
            levels.sort(key=lambda item: item.get("level") or 0)
            gear["levels"] = levels

            skills = list((gear.pop("skills", None) or []))
            for skill in skills:
                if "skill_type" not in skill:
                    skill["skill_type"] = skill.get("combat_type")
            
            # Ensure Conquest is first, Expedition is second
            skills.sort(key=lambda s: s.get("combat_type") != "Conquest")
            
            gear["skills"] = skills
            
            # Also provide as conquest_skill and expedition_skill for backwards compatibility
            skill_lookup = {"Conquest": None, "Expedition": None}
            for skill in skills:
                combat_type = skill.get("combat_type")
                if combat_type in skill_lookup:
                    skill_lookup[combat_type] = skill
            gear["conquest_skill"] = skill_lookup["Conquest"]
            gear["expedition_skill"] = skill_lookup["Expedition"]
            
            attach_public_asset_url(
                gear, path_field="image_path", url_field="image_url"
            )

        return records
    
    @staticmethod
    def _calculate_skill_tier(gear_level: int, skill_number: int) -> int:
        """
        Calculate skill tier based on gear level and skill number.
        
        Skill 1: Unlocks at level 1, upgrades at 3, 5, 7, 9 (odd levels)
        Skill 2: Unlocks at level 2, upgrades at 4, 6, 8, 10 (even levels)
        """
        if gear_level == 0:
            return 0
        
        if skill_number == 1:
            # Odd levels
            if gear_level % 2 == 1:
                return (gear_level + 1) // 2
            else:
                return gear_level // 2
        
        elif skill_number == 2:
            # Even levels, starting from 2
            if gear_level >= 2:
                if gear_level % 2 == 0:
                    return gear_level // 2
                else:
                    return (gear_level - 1) // 2
            else:
                return 0
        
        return 0
    
    @staticmethod
    def _next_skill_upgrade_level(current_level: int, skill_number: int) -> Optional[int]:
        """Calculate the next level where this skill will upgrade."""
        if current_level >= 10:
            return None
        
        if skill_number == 1:
            # Next odd level
            return current_level + 1 if current_level % 2 == 0 else current_level + 2
        elif skill_number == 2:
            # Next even level
            if current_level < 2:
                return 2
            return current_level + 1 if current_level % 2 == 1 else current_level + 2
        
        return None

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
