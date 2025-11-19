"""Repository helpers for hero talent queries."""

from __future__ import annotations

from typing import List, Optional, Tuple

from postgrest.types import CountMethod

from src.db.repository_base import BaseRepository
from src.db.utils import slugify
from src.schemas.talent import HeroTalentResponse
from supabase import Client


class TalentRepository(BaseRepository[HeroTalentResponse]):
    """Encapsulate hero talent data access."""

    _BASE_COLUMNS = "id, hero_id, name, description, icon_path"
    _SELECT_COLUMNS = (
        f"{_BASE_COLUMNS}, hero:heroes!hero_talents_hero_id_fkey(hero_id_slug, name)"
    )
    _SELECT_COLUMNS_INNER = f"{_BASE_COLUMNS}, hero:heroes!hero_talents_hero_id_fkey!inner(hero_id_slug, name)"

    def __init__(self, client: Client) -> None:
        super().__init__(client, "hero_talents", HeroTalentResponse)

    def list_filtered(
        self,
        *,
        hero_slug: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[HeroTalentResponse], int]:
        """Return talents filtered and paginated server-side."""

        select_clause = (
            self._SELECT_COLUMNS_INNER if hero_slug else self._SELECT_COLUMNS
        )
        query = (
            self.client.table(self.table_name)
            .select(select_clause, count=CountMethod.exact)
            .order("name")
        )

        if hero_slug:
            query = query.eq("hero.hero_id_slug", slugify(hero_slug))

        upper_bound = max(offset + limit - 1, offset)
        query = query.range(offset, upper_bound)

        response = query.execute()
        records = self._cast_response(response)
        hydrated = self._hydrate(records)
        total = int(response.count or 0)
        return self._to_models(hydrated), total

    def list_by_hero(self, hero_id: str) -> List[HeroTalentResponse]:
        """Return talents for a specific hero by UUID."""

        query = (
            self.client.table(self.table_name)
            .select(self._SELECT_COLUMNS)
            .eq("hero_id", hero_id)
            .order("name")
        )
        response = query.execute()
        records = self._cast_response(response)
        hydrated = self._hydrate(records)
        return self._to_models(hydrated)

    def list_by_hero_slug(self, hero_slug: str) -> List[HeroTalentResponse]:
        """Return talents for a specific hero by slug."""

        query = (
            self.client.table(self.table_name)
            .select(self._SELECT_COLUMNS_INNER)
            .eq("hero.hero_id_slug", slugify(hero_slug))
            .order("name")
        )
        response = query.execute()
        records = self._cast_response(response)
        hydrated = self._hydrate(records)
        return self._to_models(hydrated)

    @staticmethod
    def _hydrate(records: List[dict]) -> List[dict]:
        for talent in records:
            talent.pop("hero", None)
        return records
