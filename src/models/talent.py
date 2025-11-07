"""Hero talent database models."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class HeroTalentBase(BaseModel):
    """Base hero talent model."""

    model_config = ConfigDict(from_attributes=True)

    hero_id: UUID = Field(..., description="Foreign key to heroes table")
    name: str = Field(..., description="Talent name")
    description: str = Field(..., description="Talent description")
    icon_path: Optional[str] = Field(None, description="Path or URL to talent icon")


class HeroTalentCreate(HeroTalentBase):
    """Model for creating a hero talent."""

    pass


class HeroTalent(HeroTalentBase):
    """Complete hero talent model from database."""

    id: UUID = Field(..., description="Database primary key")
    created_at: Optional[datetime] = None
