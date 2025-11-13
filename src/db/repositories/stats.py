"""Repository helpers for hero stats queries."""

from __future__ import annotations

from typing import Any, Dict, List, cast

from supabase import Client


class StatsRepository:
    """Encapsulate hero stats data access."""

    def __init__(self, client: Client) -> None:
        self._client = client

    def list_all_conquest(self) -> List[Dict[str, Any]]:
        """Return all hero conquest stats with hero metadata."""

        query = (
            self._client.table("hero_conquest_stats")
            .select(
                ",".join(
                    [
                        "id",
                        "hero_id",
                        "attack",
                        "defense",
                        "health",
                        "hero:heroes!hero_conquest_stats_hero_id_fkey(id, hero_id_slug, name)",
                    ]
                )
            )
            .order("name", foreign_table="heroes")
        )
        response = query.execute()
        records = cast(List[Dict[str, Any]], response.data or [])
        for stat in records:
            hero = stat.pop("hero", None) or {}
            stat["hero_slug"] = hero.get("hero_id_slug")
            stat["hero_name"] = hero.get("name")
        return records

    def list_conquest_by_hero(self, hero_id: str) -> List[Dict[str, Any]]:
        """Return conquest stats for a specific hero."""

        query = (
            self._client.table("hero_conquest_stats")
            .select("id, hero_id, attack, defense, health")
            .eq("hero_id", hero_id)
            .order("attack")
        )
        response = query.execute()
        return cast(List[Dict[str, Any]], response.data or [])

    def list_all_expedition(self) -> List[Dict[str, Any]]:
        """Return all hero expedition stats with hero metadata."""

        query = (
            self._client.table("hero_expedition_stats")
            .select(
                ",".join(
                    [
                        "id",
                        "hero_id",
                        "troop_type",
                        "attack_pct",
                        "defense_pct",
                        "hero:heroes!hero_expedition_stats_hero_id_fkey(id, hero_id_slug, name)",
                    ]
                )
            )
            .order("name", foreign_table="heroes")
        )
        response = query.execute()
        records = cast(List[Dict[str, Any]], response.data or [])
        for stat in records:
            hero = stat.pop("hero", None) or {}
            stat["hero_slug"] = hero.get("hero_id_slug")
            stat["hero_name"] = hero.get("name")
        return records

    def list_expedition_by_hero(self, hero_id: str) -> List[Dict[str, Any]]:
        """Return expedition stats for a specific hero."""

        query = (
            self._client.table("hero_expedition_stats")
            .select("id, hero_id, troop_type, attack_pct, defense_pct")
            .eq("hero_id", hero_id)
            .order("troop_type")
        )
        response = query.execute()
        return cast(List[Dict[str, Any]], response.data or [])
