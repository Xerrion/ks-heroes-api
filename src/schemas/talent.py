"""Hero talent API schemas."""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, computed_field

from src.db.storage import build_public_asset_url


class HeroTalentResponse(BaseModel):
    """Response model for hero talent."""

    id: UUID = Field(..., description="Database primary key")
    hero_id: UUID = Field(..., description="Foreign key to heroes table")
    name: str = Field(..., description="Talent name")
    description: str = Field(..., description="Talent description")
    icon_path: Optional[str] = Field(
        None, description="Path to talent icon in storage", exclude=True
    )

    @computed_field
    @property
    def image_url(self) -> str | None:
        """Public URL for talent icon."""
        if self.icon_path:
            return build_public_asset_url(self.icon_path)
        return None

    model_config = ConfigDict(from_attributes=True)


class HeroTalentCreateRequest(BaseModel):
    """Request model for creating a hero talent."""

    hero_id: UUID = Field(..., description="Foreign key to heroes table")
    name: str = Field(..., description="Talent name")
    description: str = Field(..., description="Talent description")
    icon_path: Optional[str] = Field(None, description="Path or URL to talent icon")

    model_config = ConfigDict(from_attributes=True)


class HeroTalentListResponse(BaseModel):
    """Response for list of hero talents."""

    talents: List[HeroTalentResponse]
    total: int

    model_config = ConfigDict(from_attributes=True)
