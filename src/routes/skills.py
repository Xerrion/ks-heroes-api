"""Skills endpoints with RESTful design.

Provides:
- GET /skills - List all skills with optional filters
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from src.db.repositories.skills import SkillsRepository
from src.dependencies import get_skills_repository
from src.schemas.enums import GameMode, SkillLevel, SkillType
from src.schemas.skills import HeroSkillResponse

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("/", response_model=List[HeroSkillResponse])
def list_skills(
    hero: Optional[str] = Query(
        None, description="Filter by hero ID (e.g., 'jabel', 'olive')"
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
    skills_repo: SkillsRepository = Depends(get_skills_repository),
) -> List[HeroSkillResponse]:
    """List all skills with optional filters.

    Query parameters:
    - hero: Filter by hero ID (e.g., 'jabel', 'olive')
    - level: Filter by skill level (1-5)
    - skill_type: Filter by type (Active, Passive)
    - mode: Filter by game mode (conquest, expedition)

    Returns a list of skills matching the filters. Each skill includes all level details.
    """
    # Get skills based on hero filter
    if hero:
        skills = skills_repo.list_by_hero_slug(hero)
    else:
        skills = skills_repo.list_all()

    # Apply additional filters
    if skill_type is not None:
        skills = [s for s in skills if s.get("skill_type") == skill_type.value]

    if mode is not None:
        skills = [s for s in skills if s.get("battle_type") == mode.value.capitalize()]

    # Filter by level - this filters the levels array within each skill
    if level is not None:
        for skill in skills:
            levels = skill.get("levels", [])
            skill["levels"] = [lv for lv in levels if lv.get("level") == level.value]

    # Convert to response models
    return [HeroSkillResponse(**skill) for skill in skills]
