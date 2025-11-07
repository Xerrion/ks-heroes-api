"""Hero database models."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class HeroBase(BaseModel):
    """Base hero model."""

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    hero_id_slug: str = Field(..., description="Unique slug identifier for the hero")
    name: str = Field(..., description="Hero name")
    rarity: str = Field(..., description="Hero rarity: Rare, Epic, Mythic")
    generation: int = Field(..., ge=1, description="Hero generation number")
    class_: str = Field(
        ..., alias="class", description="Hero class: Infantry, Archer, Cavalry"
    )
    image_path: Optional[str] = Field(None, description="Path or URL to hero image")


class HeroCreate(HeroBase):
    """Model for creating a new hero."""

    pass


class HeroUpdate(BaseModel):
    """Model for updating a hero."""

    model_config = ConfigDict(populate_by_name=True)

    name: Optional[str] = None
    rarity: Optional[str] = None
    generation: Optional[int] = None
    class_: Optional[str] = Field(None, alias="class")
    image_path: Optional[str] = None


class Hero(HeroBase):
    """Complete hero model from database."""

    id: UUID = Field(..., description="Database primary key")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
