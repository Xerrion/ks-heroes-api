"""Repository for troops data access."""

from typing import List, Optional

from src.schemas.troops import Troop, TroopType
from supabase import Client


class TroopsRepository:
    """Repository for managing troops data."""

    def __init__(self, supabase: Client):
        """Initialize Troops repository with Supabase client.

        Args:
            supabase: Supabase client instance
        """
        self.supabase = supabase

    async def get_all(
        self,
        troop_type: Optional[TroopType] = None,
        min_level: int = 1,
        max_level: int = 10,
        min_tg: int = 0,
        max_tg: int = 5,
    ) -> List[Troop]:
        """Get all troops with optional filtering.

        Default returns regular troops (levels 1-10) with current TG range (0-5).
        Consumers can adjust filters to get Helios (level 11) or future TG tiers (6-10).

        Args:
            troop_type: Filter by specific troop type (Infantry/Cavalry/Archer)
            min_level: Minimum troop level (default: 1)
            max_level: Maximum troop level (default: 10, excludes Helios)
            min_tg: Minimum True Gold level (default: 0)
            max_tg: Maximum True Gold level (default: 5, current game state)

        Returns:
            List of troops matching filters
        """
        query = self.supabase.table("troops").select("*")

        if troop_type:
            query = query.eq("troop_type", troop_type.value)

        response = (
            query.gte("troop_level", min_level)
            .lte("troop_level", max_level)
            .gte("true_gold_level", min_tg)
            .lte("true_gold_level", max_tg)
            .order("troop_type")
            .order("troop_level")
            .order("true_gold_level")
            .execute()
        )

        return [Troop(**item) for item in response.data]

    async def get_by_configuration(
        self, troop_type: TroopType, troop_level: int, true_gold_level: int = 0
    ) -> Optional[Troop]:
        """Get specific troop configuration.

        Args:
            troop_type: Infantry, Cavalry, or Archer
            troop_level: Troop level (1-11)
            true_gold_level: True Gold tier (0-10)

        Returns:
            Troop data or None if not found
        """
        response = (
            self.supabase.table("troops")
            .select("*")
            .eq("troop_type", troop_type.value)
            .eq("troop_level", troop_level)
            .eq("true_gold_level", true_gold_level)
            .maybe_single()
            .execute()
        )

        return Troop(**response.data) if response.data else None
