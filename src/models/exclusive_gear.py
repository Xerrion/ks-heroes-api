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
    image_path: Optional[str] = Field(None, description="Path or URL to gear icon")


class HeroExclusiveGearCreate(HeroExclusiveGearBase):
    """Model for creating hero exclusive gear."""

    pass


class HeroExclusiveGear(HeroExclusiveGearBase):
    """Complete hero exclusive gear model from database."""

    id: UUID = Field(..., description="Database primary key")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class HeroExclusiveGearLevelBase(BaseModel):
    """Base hero exclusive gear level model."""

    model_config = ConfigDict(from_attributes=True)

    gear_id: UUID = Field(..., description="Foreign key to hero_exclusive_gear table")
    level: int = Field(..., ge=1, le=10, description="Gear level (1-10)")
    power: Optional[int] = Field(None, ge=0, description="Power rating at this level")
    hero_attack: Optional[int] = Field(None, description="Attack bonus granted")
    hero_defense: Optional[int] = Field(None, description="Defense bonus granted")
    hero_health: Optional[int] = Field(None, description="Health bonus granted")
    troop_lethality_bonus: Optional[Dict[str, Any]] = Field(
        None, description="Troop lethality bonus payload"
    )
    troop_health_bonus: Optional[Dict[str, Any]] = Field(
        None, description="Troop health bonus payload"
    )
    conquest_skill_effect: Optional[Dict[str, Any]] = Field(
        None, description="Per-level Conquest skill effect payload"
    )
    expedition_skill_effect: Optional[Dict[str, Any]] = Field(
        None, description="Per-level Expedition skill effect payload"
    )


class HeroExclusiveGearLevelCreate(HeroExclusiveGearLevelBase):
    """Model for creating hero exclusive gear level."""

    pass


class HeroExclusiveGearLevel(HeroExclusiveGearLevelBase):
    """Complete hero exclusive gear level model from database."""

    id: UUID = Field(..., description="Database primary key")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class HeroExclusiveGearSkillBase(BaseModel):
    """Base hero exclusive gear skill model."""

    model_config = ConfigDict(from_attributes=True)

    gear_id: UUID = Field(..., description="Foreign key to hero_exclusive_gear table")
    skill_type: str = Field(..., description="Skill type (Conquest or Expedition)")
    name: str = Field(..., description="Skill name")
    description: str = Field(..., description="Skill description")


class HeroExclusiveGearSkillCreate(HeroExclusiveGearSkillBase):
    """Model for creating hero exclusive gear skill."""

    pass


class HeroExclusiveGearSkill(HeroExclusiveGearSkillBase):
    """Complete hero exclusive gear skill model from database."""

    id: UUID = Field(..., description="Database primary key")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
