"""Repository for VIP levels data access."""

from typing import List, Optional

from src.db.repository_base import BaseRepository
from src.schemas.vip import VIPLevel
from supabase import Client


class VIPRepository(BaseRepository[VIPLevel]):
    """Repository for managing VIP levels data."""

    def __init__(self, client: Client):
        """Initialize VIP repository with Supabase client.

        Args:
            client: Supabase client instance
        """
        super().__init__(client, "vip_levels", VIPLevel)

    def get_all(self, min_level: int = 1, max_level: int = 12) -> List[VIPLevel]:
        """Get all VIP levels with optional range filtering.

        Args:
            min_level: Minimum VIP level (default: 1)
            max_level: Maximum VIP level (default: 12)

        Returns:
            List of VIP levels ordered by level
        """
        records, _ = self.get_filtered(
            range_filters={"level": (min_level, max_level)}, order_by="level"
        )
        return records

    def get_by_level(self, level: int) -> Optional[VIPLevel]:
        """Get specific VIP level data.

        Args:
            level: VIP level (1-12)

        Returns:
            VIP level data or None if not found
        """
        return self.get_by_id("level", level)
