"""Repository for Governor Gear data access."""

from typing import Any, Dict, List, Optional, cast

from src.schemas.governor_gear import (
    GovernorGear,
    GovernorGearCharmLevel,
    GovernorGearCharmSlot,
    GovernorGearLevel,
    GovernorGearWithCharms,
)
from supabase import Client


class GovernorGearRepository:
    """Repository for managing Governor Gear data."""

    def __init__(self, supabase: Client):
        """Initialize Governor Gear repository with Supabase client.

        Args:
            supabase: Supabase client instance
        """
        self.supabase = supabase

    # =========================================================================
    # Governor Gear Base Pieces
    # =========================================================================

    async def get_all_gear(
        self, troop_type: Optional[str] = None
    ) -> List[GovernorGear]:
        """Get all governor gear pieces with optional filtering.

        Args:
            troop_type: Filter by troop type (Infantry, Cavalry, Archer)

        Returns:
            List of governor gear pieces
        """
        query = self.supabase.table("governor_gear").select("*")

        if troop_type:
            query = query.eq("troop_type", troop_type)

        response = query.order("gear_id").execute()
        data = cast(List[Dict[str, Any]], response.data or [])
        return [GovernorGear.model_validate(item) for item in data]

    async def get_gear_by_id(self, gear_id: str) -> Optional[GovernorGear]:
        """Get specific governor gear piece by ID.

        Args:
            gear_id: Gear identifier (head, amulet, chest, legs, ring, staff)

        Returns:
            Governor gear piece or None if not found
        """
        response = (
            self.supabase.table("governor_gear")
            .select("*")
            .eq("gear_id", gear_id)
            .execute()
        )

        data = cast(List[Dict[str, Any]], response.data or [])
        if data:
            return GovernorGear.model_validate(data[0])
        return None

    async def get_gear_with_charms(
        self, gear_id: str
    ) -> Optional[GovernorGearWithCharms]:
        """Get governor gear piece with charm slot information.

        Args:
            gear_id: Gear identifier

        Returns:
            Governor gear with charm slots or None if not found
        """
        # Get base gear
        gear = await self.get_gear_by_id(gear_id)
        if not gear:
            return None

        # Get charm slots
        charm_slots = await self.get_charm_slots_by_gear(gear_id)

        # Combine into response
        gear_dict = gear.model_dump()
        gear_dict["charm_slots"] = [slot.model_dump() for slot in charm_slots]

        return GovernorGearWithCharms.model_validate(gear_dict)

    # =========================================================================
    # Governor Gear Levels
    # =========================================================================

    async def get_all_levels(
        self,
        rarity: Optional[str] = None,
        min_level: int = 1,
        max_level: int = 46,
    ) -> List[GovernorGearLevel]:
        """Get all governor gear progression levels with optional filtering.

        Args:
            rarity: Filter by rarity (Uncommon, Rare, Epic, Mythic, Legendary)
            min_level: Minimum gear level (default: 1)
            max_level: Maximum gear level (default: 46)

        Returns:
            List of governor gear levels ordered by level
        """
        query = self.supabase.table("governor_gear_levels").select("*")

        if rarity:
            query = query.eq("rarity", rarity)

        query = query.gte("level", min_level).lte("level", max_level)

        response = query.order("level").execute()
        data = cast(List[Dict[str, Any]], response.data or [])
        return [GovernorGearLevel.model_validate(item) for item in data]

    async def get_level_by_id(self, level: int) -> Optional[GovernorGearLevel]:
        """Get specific governor gear level data.

        Args:
            level: Gear level (1-46)

        Returns:
            Governor gear level data or None if not found
        """
        response = (
            self.supabase.table("governor_gear_levels")
            .select("*")
            .eq("level", level)
            .execute()
        )

        data = cast(List[Dict[str, Any]], response.data or [])
        if data:
            return GovernorGearLevel.model_validate(data[0])
        return None

    async def get_levels_by_rarity(self, rarity: str) -> List[GovernorGearLevel]:
        """Get all gear levels for a specific rarity.

        Args:
            rarity: Rarity (Uncommon, Rare, Epic, Mythic, Legendary)

        Returns:
            List of governor gear levels for that rarity
        """
        response = (
            self.supabase.table("governor_gear_levels")
            .select("*")
            .eq("rarity", rarity)
            .order("level")
            .execute()
        )

        data = cast(List[Dict[str, Any]], response.data or [])
        return [GovernorGearLevel.model_validate(item) for item in data]

    # =========================================================================
    # Governor Gear Charm Slots
    # =========================================================================

    async def get_all_charm_slots(
        self, troop_type: Optional[str] = None
    ) -> List[GovernorGearCharmSlot]:
        """Get all charm slots with optional filtering.

        Args:
            troop_type: Filter by troop type (Infantry, Cavalry, Archer)

        Returns:
            List of charm slots
        """
        query = self.supabase.table("governor_gear_charm_slots").select("*")

        if troop_type:
            query = query.eq("troop_type", troop_type)

        response = query.order("gear_id").order("slot_index").execute()
        data = cast(List[Dict[str, Any]], response.data or [])
        return [GovernorGearCharmSlot.model_validate(item) for item in data]

    async def get_charm_slots_by_gear(
        self, gear_id: str
    ) -> List[GovernorGearCharmSlot]:
        """Get charm slots for a specific gear piece.

        Args:
            gear_id: Gear identifier

        Returns:
            List of charm slots for that gear piece
        """
        response = (
            self.supabase.table("governor_gear_charm_slots")
            .select("*")
            .eq("gear_id", gear_id)
            .order("slot_index")
            .execute()
        )

        data = cast(List[Dict[str, Any]], response.data or [])
        return [GovernorGearCharmSlot.model_validate(item) for item in data]

    # =========================================================================
    # Governor Gear Charm Levels
    # =========================================================================

    async def get_all_charm_levels(
        self, min_level: int = 1, max_level: int = 16
    ) -> List[GovernorGearCharmLevel]:
        """Get all charm progression levels with optional filtering.

        Args:
            min_level: Minimum charm level (default: 1)
            max_level: Maximum charm level (default: 16)

        Returns:
            List of charm levels ordered by level
        """
        response = (
            self.supabase.table("governor_gear_charm_levels")
            .select("*")
            .gte("level", min_level)
            .lte("level", max_level)
            .order("level")
            .execute()
        )

        data = cast(List[Dict[str, Any]], response.data or [])
        return [GovernorGearCharmLevel.model_validate(item) for item in data]

    async def get_charm_level_by_id(
        self, level: int
    ) -> Optional[GovernorGearCharmLevel]:
        """Get specific charm level data.

        Args:
            level: Charm level (1-16)

        Returns:
            Charm level data or None if not found
        """
        response = (
            self.supabase.table("governor_gear_charm_levels")
            .select("*")
            .eq("level", level)
            .execute()
        )

        data = cast(List[Dict[str, Any]], response.data or [])
        if data:
            return GovernorGearCharmLevel.model_validate(data[0])
        return None
