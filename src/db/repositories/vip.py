"""Repository for VIP levels data access."""

from typing import Any, Dict, List, Optional, cast

from src.schemas.vip import VIPLevel
from supabase import Client


class VIPRepository:
    """Repository for managing VIP levels data."""

    def __init__(self, supabase: Client):
        """Initialize VIP repository with Supabase client.

        Args:
            supabase: Supabase client instance
        """
        self.supabase = supabase

    async def get_all(self, min_level: int = 1, max_level: int = 12) -> List[VIPLevel]:
        """Get all VIP levels with optional range filtering.

        Args:
            min_level: Minimum VIP level (default: 1)
            max_level: Maximum VIP level (default: 12)

        Returns:
            List of VIP levels ordered by level
        """
        response = (
            self.supabase.table("vip_levels")
            .select("*")
            .gte("level", min_level)
            .lte("level", max_level)
            .order("level")
            .execute()
        )

        data = cast(List[Dict[str, Any]], response.data or [])
        return [VIPLevel.model_validate(item) for item in data]

    async def get_by_level(self, level: int) -> Optional[VIPLevel]:
        """Get specific VIP level data.

        Args:
            level: VIP level (1-12)

        Returns:
            VIP level data or None if not found
        """
        response = (
            self.supabase.table("vip_levels").select("*").eq("level", level).execute()
        )

        data = cast(List[Dict[str, Any]], response.data or [])
        if data:
            return VIPLevel.model_validate(data[0])
        return None
