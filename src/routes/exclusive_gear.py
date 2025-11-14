"""Exclusive Gear endpoints with RESTful design.

Provides:
- GET /exclusive-gear - List all exclusive gear with optional hero filter
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from src.db.repositories.exclusive_gear import ExclusiveGearRepository
from src.dependencies import get_exclusive_gear_repository
from src.schemas.exclusive_gear import HeroExclusiveGearResponse

router = APIRouter(prefix="/exclusive-gear", tags=["exclusive-gear"])


@router.get("/", response_model=List[HeroExclusiveGearResponse])
def list_exclusive_gear(
    hero: Optional[str] = Query(
        None, description="Filter by hero slug (e.g., 'jabel', 'olive')"
    ),
    gear_repo: ExclusiveGearRepository = Depends(get_exclusive_gear_repository),
) -> List[HeroExclusiveGearResponse]:
    """List all exclusive gear with optional hero filter.

    Query parameters:
    - hero: Filter by hero slug (e.g., 'jabel', 'olive')

    Returns a list of exclusive gear with levels (1-10) and skills.
    Each gear piece includes:
    - Level stats (attack, defense, health)
    - Skills (conquest and expedition)
    - Skill tier calculations at each level
    """
    if hero:
        gear = gear_repo.list_by_hero_slug(hero)
    else:
        gear = gear_repo.list_all()

    return [HeroExclusiveGearResponse(**g) for g in gear]
