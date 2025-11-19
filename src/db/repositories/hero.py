"""Repository helpers for hero queries."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, cast

from src.db.repository_base import BaseRepository
from src.schemas.hero import HeroBasicResponse
from supabase import Client


class HeroRepository(BaseRepository[HeroBasicResponse]):
    """Encapsulate hero data access."""

    def __init__(self, client: Client) -> None:
        super().__init__(client, "heroes", HeroBasicResponse)

    def list_all(self) -> List[HeroBasicResponse]:
        """Return all heroes with their basic attributes."""
        return self.get_all(order_by="name")

    def list_filtered(
        self,
        *,
        generation: Optional[int] = None,
        rarity: Optional[str] = None,
        hero_class: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[HeroBasicResponse], int]:
        """Return heroes filtered/paginated server-side following Supabase best practices."""

        filters = {}
        if generation is not None:
            filters["generation"] = generation
        if rarity is not None:
            filters["rarity"] = rarity
        if hero_class is not None:
            filters["class"] = hero_class

        return self.get_filtered(
            filters=filters,
            limit=limit,
            offset=offset,
            order_by="name",
        )

    def get_by_slug(self, hero_slug: str) -> Optional[HeroBasicResponse]:
        """Return a single hero by slug or None when it does not exist."""
        return self.get_by_id("hero_id_slug", hero_slug)
