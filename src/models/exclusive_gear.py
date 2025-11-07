"""Hero exclusive gear database models."""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class HeroExclusiveGearBase(BaseModel):
    """Base hero exclusive gear model."""

    model_config = ConfigDict(from_attributes=True)

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


class HeroExclusiveGearCreate(HeroExclusiveGearBase):
    """Model for creating hero exclusive gear."""

    pass


class HeroExclusiveGear(HeroExclusiveGearBase):
    """Complete hero exclusive gear model from database."""

    id: UUID = Field(..., description="Database primary key")
    created_at: Optional[datetime] = None


class HeroExclusiveGearLevelBase(BaseModel):
    """Base hero exclusive gear level model."""

    model_config = ConfigDict(from_attributes=True)

    gear_id: UUID = Field(..., description="Foreign key to hero_exclusive_gear table")
    level: int = Field(..., ge=1, description="Gear level")
    power: int = Field(..., ge=0, description="Power stat")
    attack: int = Field(..., ge=0, description="Attack stat")
    defense: int = Field(..., ge=0, description="Defense stat")
    health: int = Field(..., ge=0, description="Health stat")


class HeroExclusiveGearLevelCreate(HeroExclusiveGearLevelBase):
    """Model for creating hero exclusive gear level."""

    pass


class HeroExclusiveGearLevel(HeroExclusiveGearLevelBase):
    """Complete hero exclusive gear level model from database."""

    id: UUID = Field(..., description="Database primary key")
    created_at: Optional[datetime] = None


class HeroExclusiveGearSkillBase(BaseModel):
    """Base hero exclusive gear skill model."""

    model_config = ConfigDict(from_attributes=True)

    gear_level_id: UUID = Field(
        ..., description="Foreign key to hero_exclusive_gear_levels table"
    )
    skill_number: int = Field(..., ge=1, le=2, description="Skill number (1 or 2)")
    target: str = Field(
        ..., description="Skill target (e.g., 'self', 'defender_troops')"
    )
    effect: str = Field(..., description="Skill effect type")
    value_pct: Optional[float] = Field(
        None, description="Percentage value for the effect"
    )
    troop_type: Optional[str] = Field(
        None, description="Troop type if applicable (Infantry, Archer, Cavalry)"
    )
    additional_effects: Optional[Dict[str, Any]] = Field(
        None, description="Additional effect data as JSON"
    )


class HeroExclusiveGearSkillCreate(HeroExclusiveGearSkillBase):
    """Model for creating hero exclusive gear skill."""

    pass


class HeroExclusiveGearSkill(HeroExclusiveGearSkillBase):
    """Complete hero exclusive gear skill model from database."""

    id: UUID = Field(..., description="Database primary key")
    created_at: Optional[datetime] = None
