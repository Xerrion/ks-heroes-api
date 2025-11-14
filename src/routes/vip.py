"""VIP endpoints with RESTful design.

Provides:
- GET /vip - List all VIP levels with optional range filtering
- GET /vip/{level} - Get specific VIP level
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from src.db.repositories.vip import VIPRepository
from src.dependencies import get_vip_repository
from src.schemas.vip import VIPLevel

router = APIRouter(prefix="/vip", tags=["vip"])


@router.get("/", response_model=List[VIPLevel])
async def get_all_vip_levels(
    min_level: int = Query(1, ge=1, le=12, description="Minimum VIP level"),
    max_level: int = Query(12, ge=1, le=12, description="Maximum VIP level"),
    repo: VIPRepository = Depends(get_vip_repository),
) -> List[VIPLevel]:
    """Get all VIP levels with optional range filtering.

    Returns VIP bonus data for consumption by wikis, calculators, or other tools.
    Default returns all current VIP levels (1-12).

    Args:
        min_level: Minimum VIP level to return
        max_level: Maximum VIP level to return

    Returns:
        List of VIP levels with complete bonus data
    """
    return await repo.get_all(min_level=min_level, max_level=max_level)


@router.get("/{level}", response_model=VIPLevel)
async def get_vip_level(
    level: int = Path(..., ge=1, le=12, description="VIP level"),
    repo: VIPRepository = Depends(get_vip_repository),
) -> VIPLevel:
    """Get specific VIP level bonus data.

    Args:
        level: VIP level (1-12)

    Returns:
        Complete VIP bonus data for the specified level

    Raises:
        HTTPException: 404 if VIP level not found
    """
    vip = await repo.get_by_level(level)

    if not vip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"VIP level {level} not found"
        )

    return vip
