"""Repository helpers for hero stats queries."""

from __future__ import annotations

from typing import List, Optional, Tuple

from postgrest.types import CountMethod

from src.db.repository_base import BaseRepository
from src.db.utils import slugify
from src.schemas.stats import ConquestStatsResponse, ExpeditionStatsResponse
from supabase import Client


class HeroConquestStatsRepository(BaseRepository[ConquestStatsResponse]):
    """Encapsulate conquest stat queries."""

    _JOIN_SELECT = (
        "attack, defense, health, "
        "hero:heroes!hero_conquest_stats_hero_id_fkey(hero_id_slug, name)"
    )

    def __init__(self, client: Client) -> None:
        super().__init__(client, "hero_conquest_stats", ConquestStatsResponse)

    def list_filtered(
        self,
        *,
        hero_slug: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[ConquestStatsResponse], int]:
        """Return conquest stats filtered and paginated server-side."""

        query = (
            self.client.table(self.table_name)
            .select(self._JOIN_SELECT, count=CountMethod.exact)
            .order("name", foreign_table="heroes")
        )

        if hero_slug:
            query = query.eq("hero.hero_id_slug", slugify(hero_slug))

        upper_bound = max(offset + limit - 1, offset)
        query = query.range(offset, upper_bound)

        response = query.execute()
        data = self._cast_response(response)
        self._strip_join_payload(data)
        total = int(response.count or 0)
        return self._to_models(data), total

    def list_by_hero(self, hero_id: str) -> List[ConquestStatsResponse]:
        """Return conquest stats for a specific hero by UUID."""

        query = (
            self.client.table(self.table_name)
            .select("attack, defense, health")
            .eq("hero_id", hero_id)
            .order("attack")
        )
        response = query.execute()
        data = self._cast_response(response)
        return self._to_models(data)

    def list_by_hero_slug(self, hero_slug: str) -> List[ConquestStatsResponse]:
        """Return conquest stats for a specific hero by slug."""

        query = (
            self.client.table(self.table_name)
            .select(
                "attack, defense, health, "
                "heroes!hero_conquest_stats_hero_id_fkey!inner(hero_id_slug)"
            )
            .eq("heroes.hero_id_slug", slugify(hero_slug))
            .order("attack")
        )
        response = query.execute()
        data = self._cast_response(response)
        self._strip_join_payload(data)
        return self._to_models(data)

    @staticmethod
    def _strip_join_payload(records: List[dict]) -> None:
        for stat in records:
            stat.pop("hero", None)
            stat.pop("heroes", None)


class HeroExpeditionStatsRepository(BaseRepository[ExpeditionStatsResponse]):
    """Encapsulate expedition stat queries."""

    _JOIN_SELECT = (
        "troop_type, attack_pct, defense_pct, "
        "hero:heroes!hero_expedition_stats_hero_id_fkey(hero_id_slug, name)"
    )

    def __init__(self, client: Client) -> None:
        super().__init__(client, "hero_expedition_stats", ExpeditionStatsResponse)

    def list_filtered(
        self,
        *,
        hero_slug: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[ExpeditionStatsResponse], int]:
        """Return expedition stats filtered and paginated server-side."""

        query = (
            self.client.table(self.table_name)
            .select(self._JOIN_SELECT, count=CountMethod.exact)
            .order("name", foreign_table="heroes")
        )

        if hero_slug:
            query = query.eq("hero.hero_id_slug", slugify(hero_slug))

        upper_bound = max(offset + limit - 1, offset)
        query = query.range(offset, upper_bound)

        response = query.execute()
        data = self._cast_response(response)
        self._strip_join_payload(data)
        total = int(response.count or 0)
        return self._to_models(data), total

    def list_by_hero(self, hero_id: str) -> List[ExpeditionStatsResponse]:
        """Return expedition stats for a specific hero by UUID."""

        query = (
            self.client.table(self.table_name)
            .select("troop_type, attack_pct, defense_pct")
            .eq("hero_id", hero_id)
            .order("troop_type")
        )
        response = query.execute()
        data = self._cast_response(response)
        return self._to_models(data)

    def list_by_hero_slug(self, hero_slug: str) -> List[ExpeditionStatsResponse]:
        """Return expedition stats for a specific hero by slug."""

        query = (
            self.client.table(self.table_name)
            .select(
                "troop_type, attack_pct, defense_pct, "
                "heroes!hero_expedition_stats_hero_id_fkey!inner(hero_id_slug)"
            )
            .eq("heroes.hero_id_slug", slugify(hero_slug))
            .order("troop_type")
        )
        response = query.execute()
        data = self._cast_response(response)
        self._strip_join_payload(data)
        return self._to_models(data)

    @staticmethod
    def _strip_join_payload(records: List[dict]) -> None:
        for stat in records:
            stat.pop("hero", None)
            stat.pop("heroes", None)
