"""Exclusive Gear endpoints with RESTful design.

Provides:
- GET /exclusive-gear - List all exclusive gear with optional hero filter
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from src.db.repositories.exclusive_gear import ExclusiveGearRepository
from src.dependencies import get_exclusive_gear_repository
from src.schemas.exclusive_gear import HeroExclusiveGearListResponse

router = APIRouter(prefix="/exclusive-gear", tags=["exclusive-gear"])


@router.get("/", response_model=HeroExclusiveGearListResponse)
def list_exclusive_gear(
    hero: Optional[str] = Query(
        None, description="Filter by hero slug (e.g., 'jabel', 'olive')"
    ),
    limit: int = Query(25, ge=1, le=50, description="Maximum gear items to return"),
    offset: int = Query(0, ge=0, description="Number of gear items to skip"),
    gear_repo: ExclusiveGearRepository = Depends(get_exclusive_gear_repository),
) -> HeroExclusiveGearListResponse:
    """List all exclusive gear with optional hero filter.

    Query parameters:
    - hero: Filter by hero slug (e.g., 'jabel', 'olive')
    - limit/offset: Pagination controls

    Returns a paginated list of exclusive gear with levels and skills.
    """
    gear, total = gear_repo.list_filtered(
        hero_slug=hero,
        limit=limit,
        offset=offset,
    )
    return HeroExclusiveGearListResponse(gear=gear, total=total)
