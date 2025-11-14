"""Hero exclusive gear API schemas."""

from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class HeroExclusiveGearSkillResponse(BaseModel):
    """Response model for exclusive gear skill."""

    battle_type: str = Field(..., description="Battle type (Conquest or Expedition)")
    name: str = Field(..., description="Skill name")
    description: Optional[str] = Field(None, description="Skill description")

    class Config:
        from_attributes = True


class HeroExclusiveGearLevelResponse(BaseModel):
    """Response model for exclusive gear level."""

    level: int = Field(..., ge=1, le=10, description="Gear level (1-10)")
    power: int = Field(..., ge=0, description="Power rating at this level")
    hero_attack: int = Field(..., description="Attack bonus at this level")
    hero_defense: int = Field(..., description="Defense bonus at this level")
    hero_health: int = Field(..., description="Health bonus at this level")
    troop_lethality_bonus: Optional[Dict[str, Any]] = Field(
        None, description="Troop lethality bonus payload"
    )
    troop_health_bonus: Optional[Dict[str, Any]] = Field(
        None, description="Troop health bonus payload"
    )
    conquest_skill_effect: Optional[Dict[str, Any]] = Field(
        None, description="Conquest skill effect payload"
    )
    expedition_skill_effect: Optional[Dict[str, Any]] = Field(
        None, description="Expedition skill effect payload"
    )

    class Config:
        from_attributes = True


class HeroExclusiveGearResponse(BaseModel):
    """Response model for hero exclusive gear with all levels."""

    name: str = Field(..., description="Exclusive gear name")
    hero_slug: Optional[str] = Field(None, description="Hero slug identifier")
    hero_name: Optional[str] = Field(None, description="Hero name")
    image_path: Optional[str] = Field(None, description="Path or URL to gear icon")
    image_url: Optional[str] = Field(None, description="Public URL to gear icon")
    is_unlocked: bool = Field(
        default=False, description="Whether the gear has been unlocked"
    )
    current_level: int = Field(
        default=0, ge=0, le=10, description="Current gear level (0-10)"
    )
    levels: Optional[List[HeroExclusiveGearLevelResponse]] = Field(
        None, description="Gear levels with stats"
    )
    conquest_skill: Optional[HeroExclusiveGearSkillResponse] = Field(
        None, description="Conquest skill metadata"
    )
    expedition_skill: Optional[HeroExclusiveGearSkillResponse] = Field(
        None, description="Expedition skill metadata"
    )

    class Config:
        from_attributes = True


class HeroExclusiveGearProgressionResponse(BaseModel):
    """Detailed progression info for exclusive gear."""

    gear_id: UUID = Field(..., description="Gear ID")
    hero_id: UUID = Field(..., description="Hero ID")
    gear_name: str = Field(..., description="Gear name")
    is_unlocked: bool = Field(..., description="Whether gear is unlocked")
    current_level: int = Field(..., ge=0, le=10, description="Current gear level")
    max_level: int = Field(default=10, description="Maximum gear level")

    # Current stats at current level
    current_power: Optional[int] = Field(None, description="Current power")
    current_hero_attack: Optional[int] = Field(None, description="Current attack bonus")
    current_hero_defense: Optional[int] = Field(
        None, description="Current defense bonus"
    )
    current_hero_health: Optional[int] = Field(None, description="Current health bonus")

    # Skill 1 progression
    skill_1_name: Optional[str] = Field(None, description="First skill name")
    skill_1_battle_type: Optional[str] = Field(None, description="Skill 1 battle type")
    skill_1_current_tier: int = Field(
        default=0, ge=0, le=5, description="Current tier of first skill"
    )
    skill_1_max_tier: int = Field(default=5, description="Max tier of first skill")
    skill_1_next_upgrade_at_level: Optional[int] = Field(
        None, description="Next level where skill 1 upgrades"
    )

    # Skill 2 progression
    skill_2_name: Optional[str] = Field(None, description="Second skill name")
    skill_2_battle_type: Optional[str] = Field(None, description="Skill 2 battle type")
    skill_2_current_tier: int = Field(
        default=0, ge=0, le=5, description="Current tier of second skill"
    )
    skill_2_max_tier: int = Field(default=5, description="Max tier of second skill")
    skill_2_next_upgrade_at_level: Optional[int] = Field(
        None, description="Next level where skill 2 upgrades"
    )

    # What happens at next level
    next_level: Optional[int] = Field(None, description="Next gear level")
    next_level_unlocks: Optional[str] = Field(
        None, description="What unlocks at next level"
    )

    class Config:
        from_attributes = True


class HeroExclusiveGearCreateRequest(BaseModel):
    """Request model for creating hero exclusive gear."""

    hero_id: UUID = Field(..., description="Foreign key to heroes table")
    name: str = Field(..., description="Exclusive gear name")
    image_path: Optional[str] = Field(None, description="Path or URL to gear icon")

    class Config:
        from_attributes = True


class HeroExclusiveGearLevelCreateRequest(BaseModel):
    """Request model for creating exclusive gear level."""

    gear_id: UUID = Field(..., description="Foreign key to hero_exclusive_gear table")
    level: int = Field(..., ge=1, le=10, description="Gear level")
    power: Optional[int] = Field(None, ge=0, description="Power rating at this level")
    hero_attack: Optional[int] = Field(None, description="Attack bonus at this level")
    hero_defense: Optional[int] = Field(None, description="Defense bonus at this level")
    hero_health: Optional[int] = Field(None, description="Health bonus at this level")
    troop_lethality_bonus: Optional[Dict[str, Any]] = Field(
        None, description="Troop lethality bonus payload"
    )
    troop_health_bonus: Optional[Dict[str, Any]] = Field(
        None, description="Troop health bonus payload"
    )
    conquest_skill_effect: Optional[Dict[str, Any]] = Field(
        None, description="Conquest skill effect payload"
    )
    expedition_skill_effect: Optional[Dict[str, Any]] = Field(
        None, description="Expedition skill effect payload"
    )

    class Config:
        from_attributes = True


class HeroExclusiveGearSkillCreateRequest(BaseModel):
    """Request model for creating exclusive gear skill."""

    gear_id: UUID = Field(..., description="Foreign key to hero_exclusive_gear table")
    skill_type: str = Field(..., description="Skill type (Conquest or Expedition)")
    name: str = Field(..., description="Skill name")
    description: str = Field(..., description="Skill description")

    class Config:
        from_attributes = True
