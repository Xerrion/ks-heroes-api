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

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from src.db.repositories.governor_gear import GovernorGearRepository
from src.dependencies import get_governor_gear_repository
from src.schemas.enums import GearRarity, HeroClass
from src.schemas.governor_gear import (
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
