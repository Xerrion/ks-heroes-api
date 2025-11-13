"""Hero API schemas."""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from .exclusive_gear import HeroExclusiveGearResponse
from .skills import HeroSkillResponse
from .stats import HeroExpeditionStatsResponse, HeroStatsResponse
from .talent import HeroTalentResponse


class HeroBasicResponse(BaseModel):
    """Basic hero response without nested data."""

    id: UUID = Field(..., description="Database primary key")
    hero_id_slug: str = Field(..., description="Unique slug identifier for the hero")
    name: str = Field(..., description="Hero name")
    rarity: str = Field(..., description="Hero rarity: Rare, Epic, Mythic")
    generation: int = Field(..., description="Hero generation number")
    class_: str = Field(
        ..., alias="class", description="Hero class: Infantry, Archer, Cavalry"
    )
    image_path: Optional[str] = Field(None, description="Path or URL to hero image")
    image_url: Optional[str] = Field(None, description="Public URL to hero image")

    class Config:
        populate_by_name = True
        from_attributes = True


class HeroListResponse(BaseModel):
    """Response for list of heroes."""

    heroes: List[HeroBasicResponse]
    total: int

    class Config:
        from_attributes = True


class HeroDetailResponse(HeroBasicResponse):
    """Detailed hero response with all nested data."""

    conquest_stats: Optional[List[HeroStatsResponse]] = Field(
        None, description="Conquest stats by level"
    )
    expedition_stats: Optional[List[HeroExpeditionStatsResponse]] = Field(
        None, description="Expedition stats by level"
    )
    conquest_skills: Optional[List[HeroSkillResponse]] = Field(
        None, description="Conquest skills"
    )
    expedition_skills: Optional[List[HeroSkillResponse]] = Field(
        None, description="Expedition skills"
    )
    exclusive_gear: Optional[HeroExclusiveGearResponse] = Field(
        None, description="Exclusive gear data"
    )
    talents: Optional[List[HeroTalentResponse]] = Field(
        None, description="Hero talents"
    )

    class Config(HeroBasicResponse.Config):
        pass


class HeroCreateRequest(BaseModel):
    """Request model for creating a hero."""

    hero_id_slug: str = Field(..., description="Unique slug identifier for the hero")
    name: str = Field(..., description="Hero name")
    rarity: str = Field(..., description="Hero rarity: Rare, Epic, Mythic")
    generation: int = Field(..., ge=1, description="Hero generation number")
    class_: str = Field(
        ..., alias="class", description="Hero class: Infantry, Archer, Cavalry"
    )
    image_path: Optional[str] = Field(None, description="Path or URL to hero image")

    class Config:
        populate_by_name = True


class HeroUpdateRequest(BaseModel):
    """Request model for updating a hero."""

    name: Optional[str] = None
    rarity: Optional[str] = None
    generation: Optional[int] = Field(None, ge=1)
    class_: Optional[str] = Field(None, alias="class")
    image_path: Optional[str] = None

    class Config:
        populate_by_name = True
