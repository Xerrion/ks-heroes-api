"""Hero exclusive gear API schemas."""

from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class HeroExclusiveGearSkillResponse(BaseModel):
    """Response model for exclusive gear skill."""

    skill_number: int = Field(..., description="Skill number (1 or 2)")
    target: str = Field(..., description="Skill target")
    effect: str = Field(..., description="Skill effect type")
    value_pct: Optional[float] = Field(
        None, description="Percentage value for the effect"
    )
    troop_type: Optional[str] = Field(None, description="Troop type if applicable")
    additional_effects: Optional[Dict[str, Any]] = Field(
        None, description="Additional effect data"
    )

    class Config:
        from_attributes = True


class HeroExclusiveGearLevelResponse(BaseModel):
    """Response model for exclusive gear level."""

    level: int = Field(..., description="Gear level")
    power: int = Field(..., description="Power stat")
    attack: int = Field(..., description="Attack stat")
    defense: int = Field(..., description="Defense stat")
    health: int = Field(..., description="Health stat")
    skills: Optional[List[HeroExclusiveGearSkillResponse]] = Field(
        None, description="Gear skills at this level"
    )

    class Config:
        from_attributes = True


class HeroExclusiveGearResponse(BaseModel):
    """Response model for hero exclusive gear with all levels."""

    id: UUID = Field(..., description="Database primary key")
    hero_id: UUID = Field(..., description="Foreign key to heroes table")
    name: str = Field(..., description="Exclusive gear name")
    conquest_skill_name: str = Field(..., description="Conquest skill name")
    conquest_skill_description: str = Field(
        ..., description="Conquest skill description"
    )
    expedition_skill_name: str = Field(..., description="Expedition skill name")
    expedition_skill_description: str = Field(
        ..., description="Expedition skill description"
    )
    icon_path: Optional[str] = Field(None, description="Path or URL to gear icon")
    levels: Optional[List[HeroExclusiveGearLevelResponse]] = Field(
        None, description="Gear levels with stats and skills"
    )

    class Config:
        from_attributes = True


class HeroExclusiveGearCreateRequest(BaseModel):
    """Request model for creating hero exclusive gear."""

    hero_id: UUID = Field(..., description="Foreign key to heroes table")
    name: str = Field(..., description="Exclusive gear name")
    conquest_skill_name: str = Field(..., description="Conquest skill name")
    conquest_skill_description: str = Field(
        ..., description="Conquest skill description"
    )
    expedition_skill_name: str = Field(..., description="Expedition skill name")
    expedition_skill_description: str = Field(
        ..., description="Expedition skill description"
    )
    icon_path: Optional[str] = Field(None, description="Path or URL to gear icon")

    class Config:
        from_attributes = True


class HeroExclusiveGearLevelCreateRequest(BaseModel):
    """Request model for creating exclusive gear level."""

    gear_id: UUID = Field(..., description="Foreign key to hero_exclusive_gear table")
    level: int = Field(..., ge=1, description="Gear level")
    power: int = Field(..., ge=0, description="Power stat")
    attack: int = Field(..., ge=0, description="Attack stat")
    defense: int = Field(..., ge=0, description="Defense stat")
    health: int = Field(..., ge=0, description="Health stat")

    class Config:
        from_attributes = True


class HeroExclusiveGearSkillCreateRequest(BaseModel):
    """Request model for creating exclusive gear skill."""

    gear_level_id: UUID = Field(
        ..., description="Foreign key to hero_exclusive_gear_levels table"
    )
    skill_number: int = Field(..., ge=1, le=2, description="Skill number (1 or 2)")
    target: str = Field(..., description="Skill target")
    effect: str = Field(..., description="Skill effect type")
    value_pct: Optional[float] = Field(
        None, description="Percentage value for the effect"
    )
    troop_type: Optional[str] = Field(None, description="Troop type if applicable")
    additional_effects: Optional[Dict[str, Any]] = Field(
        None, description="Additional effect data"
    )

    class Config:
        from_attributes = True
