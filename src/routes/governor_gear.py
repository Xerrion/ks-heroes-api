"""Governor Gear endpoints with RESTful design.

Provides:
- GET /governor-gear - List all governor gear pieces
- GET /governor-gear/{gear_id} - Get specific gear piece with charm slots
- GET /governor-gear/levels - List all gear progression levels
- GET /governor-gear/levels/{level} - Get specific gear level
- GET /governor-gear/charms - List all charm slots
- GET /governor-gear/charms/levels - List all charm progression levels
- GET /governor-gear/charms/levels/{level} - Get specific charm level
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from src.db.repositories.governor_gear import GovernorGearRepository
from src.dependencies import get_governor_gear_repository
from src.schemas.enums import GearRarity, HeroClass
from src.schemas.governor_gear import (
    GearConfiguration,
    GearStatsBreakdown,
    GearStatsCalculation,
    GovernorGear,
    GovernorGearCharmLevel,
    GovernorGearCharmSlot,
    GovernorGearLevel,
    GovernorGearWithCharms,
)

router = APIRouter(prefix="/governor-gear", tags=["governor-gear"])


# =============================================================================
# Governor Gear Base Pieces
# =============================================================================


@router.get("/", response_model=List[GovernorGear])
async def get_all_gear(
    troop_type: Optional[HeroClass] = Query(
        None, description="Filter by troop type (Infantry, Cavalry, Archer)"
    ),
    repo: GovernorGearRepository = Depends(get_governor_gear_repository),
) -> List[GovernorGear]:
    """Get all governor gear pieces with optional filtering.

    Returns base governor gear information including slot, troop type, and charm capacity.

    Args:
        troop_type: Optional filter by troop type

    Returns:
        List of governor gear pieces (head, amulet, chest, legs, ring, staff)
    """
    return await repo.get_all_gear(troop_type=troop_type.value if troop_type else None)


@router.get("/{gear_id}", response_model=GovernorGearWithCharms)
async def get_gear_by_id(
    gear_id: str = Path(
        ..., description="Gear identifier (head, amulet, chest, legs, ring, staff)"
    ),
    repo: GovernorGearRepository = Depends(get_governor_gear_repository),
) -> GovernorGearWithCharms:
    """Get specific governor gear piece with charm slot information.

    Args:
        gear_id: Gear identifier

    Returns:
        Governor gear piece with charm slots

    Raises:
        HTTPException: 404 if gear piece not found
    """
    gear = await repo.get_gear_with_charms(gear_id)

    if not gear:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Governor gear '{gear_id}' not found",
        )

    return gear


# =============================================================================
# Governor Gear Levels
# =============================================================================


@router.get("/levels/", response_model=List[GovernorGearLevel])
async def get_all_levels(
    rarity: Optional[GearRarity] = Query(
        None, description="Filter by rarity (Uncommon, Rare, Epic, Mythic, Legendary)"
    ),
    min_level: int = Query(1, ge=1, le=46, description="Minimum gear level"),
    max_level: int = Query(46, ge=1, le=46, description="Maximum gear level"),
    repo: GovernorGearRepository = Depends(get_governor_gear_repository),
) -> List[GovernorGearLevel]:
    """Get all governor gear progression levels with optional filtering.

    Returns gear level data including rarity, tier, stars, name, and stat bonuses.
    Useful for progression calculators and stat analysis.

    Args:
        rarity: Optional filter by rarity
        min_level: Minimum gear level to return
        max_level: Maximum gear level to return

    Returns:
        List of gear levels with complete progression data
    """
    return await repo.get_all_levels(
        rarity=rarity.value if rarity else None,
        min_level=min_level,
        max_level=max_level,
    )


@router.get("/levels/{level}", response_model=GovernorGearLevel)
async def get_level_by_id(
    level: int = Path(..., ge=1, le=46, description="Gear level (1-46)"),
    repo: GovernorGearRepository = Depends(get_governor_gear_repository),
) -> GovernorGearLevel:
    """Get specific governor gear level data.

    Args:
        level: Gear level

    Returns:
        Complete gear level data including bonuses

    Raises:
        HTTPException: 404 if gear level not found
    """
    gear_level = await repo.get_level_by_id(level)

    if not gear_level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Governor gear level {level} not found",
        )

    return gear_level


# =============================================================================
# Governor Gear Charm Slots
# =============================================================================


@router.get("/charms/", response_model=List[GovernorGearCharmSlot])
async def get_all_charm_slots(
    troop_type: Optional[HeroClass] = Query(
        None, description="Filter by troop type (Infantry, Cavalry, Archer)"
    ),
    repo: GovernorGearRepository = Depends(get_governor_gear_repository),
) -> List[GovernorGearCharmSlot]:
    """Get all charm slots with optional filtering.

    Returns charm slot definitions including which stats they provide.

    Args:
        troop_type: Optional filter by troop type

    Returns:
        List of charm slots (18 total: 6 gear pieces × 3 slots each)
    """
    return await repo.get_all_charm_slots(
        troop_type=troop_type.value if troop_type else None
    )


# =============================================================================
# Governor Gear Charm Levels
# =============================================================================


@router.get("/charms/levels/", response_model=List[GovernorGearCharmLevel])
async def get_all_charm_levels(
    min_level: int = Query(1, ge=1, le=16, description="Minimum charm level"),
    max_level: int = Query(16, ge=1, le=16, description="Maximum charm level"),
    repo: GovernorGearRepository = Depends(get_governor_gear_repository),
) -> List[GovernorGearCharmLevel]:
    """Get all charm progression levels with optional filtering.

    Returns charm level data with stat bonuses per level.

    Args:
        min_level: Minimum charm level to return
        max_level: Maximum charm level to return

    Returns:
        List of charm levels with complete bonus data
    """
    return await repo.get_all_charm_levels(min_level=min_level, max_level=max_level)


@router.get("/charms/levels/{level}", response_model=GovernorGearCharmLevel)
async def get_charm_level_by_id(
    level: int = Path(..., ge=1, le=16, description="Charm level (1-16)"),
    repo: GovernorGearRepository = Depends(get_governor_gear_repository),
) -> GovernorGearCharmLevel:
    """Get specific charm level data.

    Args:
        level: Charm level

    Returns:
        Complete charm level data including bonuses

    Raises:
        HTTPException: 404 if charm level not found
    """
    charm_level = await repo.get_charm_level_by_id(level)

    if not charm_level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Governor gear charm level {level} not found",
        )

    return charm_level


# =============================================================================
# Governor Gear Calculator
# =============================================================================


@router.post("/calculate-stats", response_model=GearStatsCalculation)
async def calculate_gear_stats(
    config: List[GearConfiguration],
    repo: GovernorGearRepository = Depends(get_governor_gear_repository),
) -> GearStatsCalculation:
    """Calculate total stats for a given gear configuration.

    Args:
        config: List of gear configurations (gear piece, rarity, stars, gems)

    Returns:
        Total calculated stats and breakdown
    """
    # Fetch all necessary data
    # Note: In a production environment, these should be cached
    all_gear = await repo.get_all_gear()
    levels = await repo.get_all_levels()
    charm_levels = await repo.get_all_charm_levels()
    charm_slots = await repo.get_all_charm_slots()

    # Create lookup maps
    # gear_id -> GovernorGear
    gear_map = {g.gear_id: g for g in all_gear}

    # (rarity, tier, stars) -> GovernorGearLevel
    levels_map = {(l.rarity, l.tier, l.stars): l for l in levels}

    # level -> GovernorGearCharmLevel
    charm_levels_map = {l.level: l for l in charm_levels}

    # (gear_id, slot_index) -> GovernorGearCharmSlot
    charm_slots_map = {(s.gear_id, s.slot_index): s for s in charm_slots}

    total_bonuses: Dict[str, Dict[str, float]] = {}
    breakdown: List[GearStatsBreakdown] = []

    def add_to_total(key: str, val: float, t_type: Optional[HeroClass]) -> None:
        """Helper to aggregate bonuses into nested structure."""
        if key.startswith("troop_") and t_type:
            group = t_type.value.lower()
            stat = key.replace("troop_", "", 1)
        else:
            group = "general"
            stat = key

        if group not in total_bonuses:
            total_bonuses[group] = {}
        total_bonuses[group][stat] = total_bonuses[group].get(stat, 0.0) + val

    for item in config:
        current_gear_bonuses: Dict[str, float] = {}
        current_gem_bonuses: Dict[str, float] = {}
        errors: List[str] = []

        # 1. Calculate Gear Bonuses
        gear_level = levels_map.get((item.rarity, item.tier, item.stars))
        gear_info = gear_map.get(item.gear_id)

        if gear_level and gear_info:
            for key, value in gear_level.bonuses.items():
                # Normalize key for breakdown (e.g. attack_pct -> troop_attack_pct)
                breakdown_key = key
                if key in ["attack_pct", "defense_pct", "health_pct"]:
                    breakdown_key = f"troop_{key}"

                current_gear_bonuses[breakdown_key] = (
                    current_gear_bonuses.get(breakdown_key, 0.0) + value
                )

                # Add to total bonuses
                add_to_total(breakdown_key, value, gear_info.troop_type)
        else:
            if not gear_level:
                errors.append(
                    f"Level not found for {item.rarity} T{item.tier} {item.stars}*"
                )
            if not gear_info:
                errors.append(f"Gear info not found for {item.gear_id}")

        # 2. Calculate Gem Bonuses
        for i, gem_level_val in enumerate(item.gem_levels):
            slot_index = i + 1  # 1-based index

            # Get slot definition
            slot = charm_slots_map.get((item.gear_id, slot_index))
            if not slot:
                errors.append(f"Slot {slot_index} not found for {item.gear_id}")
                continue

            # Get gem level data
            gem_data = charm_levels_map.get(gem_level_val)
            if not gem_data:
                errors.append(f"Gem level {gem_level_val} not found")
                continue

            # Apply bonuses based on slot keys
            for key in slot.bonus_keys:
                # We assume the gem data has the value for this key
                # If not, we might need a fallback or it's 0
                value = gem_data.bonuses.get(key, 0.0)
                if value > 0:
                    # Keep generic key for breakdown (e.g. troop_lethality_pct)
                    current_gem_bonuses[key] = current_gem_bonuses.get(key, 0.0) + value

                    # Add to total bonuses
                    add_to_total(key, value, slot.troop_type)

        breakdown.append(
            GearStatsBreakdown(
                gear_id=item.gear_id,
                troop_type=gear_info.troop_type if gear_info else None,
                gear_bonus=current_gear_bonuses,
                gem_bonus=current_gem_bonuses,
                errors=errors,
            )
        )

    return GearStatsCalculation(total_bonuses=total_bonuses, breakdown=breakdown)
