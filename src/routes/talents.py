"""Talents endpoints with RESTful design.

Provides:
- GET /talents - List all talents with optional hero filter
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query

from src.db.repositories.talent import TalentRepository
from src.dependencies import get_talent_repository
from src.schemas.talent import HeroTalentListResponse

router = APIRouter(prefix="/talents", tags=["talents"])


@router.get("/", response_model=HeroTalentListResponse)
def list_talents(
    hero: Optional[str] = Query(
        None, description="Filter by hero slug (e.g., 'jabel', 'olive')"
    ),
    limit: int = Query(
        50, ge=1, le=100, description="Maximum number of talents to return (max 100)"
    ),
    offset: int = Query(0, ge=0, description="Number of talents to skip"),
    talent_repo: TalentRepository = Depends(get_talent_repository),
) -> HeroTalentListResponse:
    """List all hero talents with optional hero filter.

    Query parameters:
    - hero: Filter by hero slug (e.g., 'jabel', 'olive')
    - limit/offset: Pagination controls

    Returns a paginated list of talents.
    """
    talents, total = talent_repo.list_filtered(
        hero_slug=hero,
        limit=limit,
        offset=offset,
    )
    return HeroTalentListResponse(talents=talents, total=total)
