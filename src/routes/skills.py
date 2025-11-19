"""Skills endpoints with RESTful design.

Provides:
- GET /skills - List all skills with optional filters
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query

from src.db.repositories.skills import SkillsRepository
from src.dependencies import get_skills_repository
from src.schemas.enums import GameMode, SkillLevel, SkillType
from src.schemas.skills import HeroSkillListResponse, HeroSkillResponse

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("/", response_model=HeroSkillListResponse)
def list_skills(
    hero: Optional[str] = Query(
        None, description="Filter by hero slug (e.g., 'jabel', 'olive')"
    ),
    level: Optional[SkillLevel] = Query(
        None, description="Filter by skill level (1-5)"
    ),
    skill_type: Optional[SkillType] = Query(
        None, description="Filter by skill type (Active, Passive)"
    ),
    mode: Optional[GameMode] = Query(
        None, description="Filter by game mode (conquest, expedition)"
    ),
    limit: int = Query(
        50, ge=1, le=100, description="Maximum number of skills to return (max 100)"
    ),
    offset: int = Query(0, ge=0, description="Number of skills to skip"),
    skills_repo: SkillsRepository = Depends(get_skills_repository),
) -> HeroSkillListResponse:
    """List all skills with optional filters.

    Query parameters:
    - hero: Filter by hero slug (e.g., 'jabel', 'olive')
    - level: Filter by skill level (1-5)
    - skill_type: Filter by type (Active, Passive)
    - mode: Filter by game mode (conquest, expedition)
    - limit/offset: Pagination controls

    Returns a paginated list of skills matching the filters.
    """
    battle_type = mode.value.capitalize() if mode else None
    skills, total = skills_repo.list_filtered(
        hero_slug=hero,
        skill_type=skill_type.value if skill_type else None,
        battle_type=battle_type,
        limit=limit,
        offset=offset,
    )

    # Filter by level - this filters the levels array within each skill
    if level is not None:
        filtered_skills = []
        for skill in skills:
            levels = skill.levels or []
            skill.levels = [lv for lv in levels if lv.level == level.value]
            if skill.levels:
                filtered_skills.append(skill)
        skills = filtered_skills
        total = len(skills)

    return HeroSkillListResponse(skills=skills, total=total)
