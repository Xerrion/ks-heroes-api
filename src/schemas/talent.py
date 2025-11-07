"""Hero talent API schemas."""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class HeroTalentResponse(BaseModel):
    """Response model for hero talent."""

    id: UUID = Field(..., description="Database primary key")
    hero_id: UUID = Field(..., description="Foreign key to heroes table")
    name: str = Field(..., description="Talent name")
    description: str = Field(..., description="Talent description")
    icon_path: Optional[str] = Field(None, description="Path or URL to talent icon")

    class Config:
        from_attributes = True


class HeroTalentCreateRequest(BaseModel):
    """Request model for creating a hero talent."""

    hero_id: UUID = Field(..., description="Foreign key to heroes table")
    name: str = Field(..., description="Talent name")
    description: str = Field(..., description="Talent description")
    icon_path: Optional[str] = Field(None, description="Path or URL to talent icon")

    class Config:
        from_attributes = True


class HeroTalentListResponse(BaseModel):
    """Response for list of hero talents."""

    talents: List[HeroTalentResponse]
    total: int

    class Config:
        from_attributes = True
