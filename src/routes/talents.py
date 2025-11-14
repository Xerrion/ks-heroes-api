"""Talents endpoints with RESTful design.

Provides:
- GET /talents - List all talents with optional hero filter
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from src.db.repositories.talent import TalentRepository
from src.dependencies import get_talent_repository
from src.schemas.talent import HeroTalentResponse

router = APIRouter(prefix="/talents", tags=["talents"])


@router.get("/", response_model=List[HeroTalentResponse])
def list_talents(
    hero: Optional[str] = Query(
        None, description="Filter by hero ID (e.g., 'jabel', 'olive')"
    ),
    talent_repo: TalentRepository = Depends(get_talent_repository),
) -> List[HeroTalentResponse]:
    """List all hero talents with optional hero filter.

    Query parameters:
    - hero: Filter by hero ID (e.g., 'jabel', 'olive')

    Returns a list of talents. Each hero typically has multiple talents
    that provide various bonuses and effects.
    """
    if hero:
        talents = talent_repo.list_by_hero_slug(hero)
    else:
        talents = talent_repo.list_all()

    return [HeroTalentResponse(**talent) for talent in talents]
