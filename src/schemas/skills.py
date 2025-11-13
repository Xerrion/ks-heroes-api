"""Hero skills API schemas."""

from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class HeroSkillLevelResponse(BaseModel):
    """Response model for hero skill level."""

    level: int = Field(..., description="Skill level (1-5)")
    effects: Dict[str, Any] = Field(..., description="Skill effects as key-value pairs")

    class Config:
        from_attributes = True


class HeroSkillResponse(BaseModel):
    """Response model for hero skill with all levels."""

    id: UUID = Field(..., description="Database primary key")
    hero_id: UUID = Field(..., description="Foreign key to heroes table")
    name: str = Field(..., description="Skill name")
    skill_type: str = Field(..., description="Skill type: Active, Passive")
    battle_type: str = Field(..., description="Battle type: Conquest, Expedition")
    description: str = Field(..., description="Skill description")
    icon_path: Optional[str] = Field(None, description="Path or URL to skill icon")
    icon_url: Optional[str] = Field(None, description="Public URL to skill icon")
    levels: Optional[List[HeroSkillLevelResponse]] = Field(
        None, description="Skill levels with effects"
    )

    class Config:
        from_attributes = True


class HeroSkillCreateRequest(BaseModel):
    """Request model for creating a hero skill."""

    hero_id: UUID = Field(..., description="Foreign key to heroes table")
    name: str = Field(..., description="Skill name")
    skill_type: str = Field(..., description="Skill type: Active, Passive")
    battle_type: str = Field(..., description="Battle type: Conquest, Expedition")
    description: str = Field(..., description="Skill description")
    icon_path: Optional[str] = Field(None, description="Path or URL to skill icon")

    class Config:
        from_attributes = True


class HeroSkillLevelCreateRequest(BaseModel):
    """Request model for creating a hero skill level."""

    skill_id: UUID = Field(..., description="Foreign key to hero_skills table")
    level: int = Field(..., ge=1, le=5, description="Skill level (1-5)")
    effects: Dict[str, Any] = Field(..., description="Skill effects as key-value pairs")

    class Config:
        from_attributes = True


class HeroSkillListResponse(BaseModel):
    """Response for list of hero skills."""

    skills: List[HeroSkillResponse]
    total: int

    class Config:
        from_attributes = True
