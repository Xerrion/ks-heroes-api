"""Hero skills database models."""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, computed_field

from src.db.storage import build_public_asset_url, resolve_asset_path
from src.db.utils import slugify


class HeroSkillBase(BaseModel):
    """Base hero skill model."""

    model_config = ConfigDict(from_attributes=True)

    hero_id: UUID = Field(..., description="Foreign key to heroes table")
    name: str = Field(..., description="Skill name")
    skill_type: str = Field(..., description="Skill type: Active, Passive")
    battle_type: str = Field(..., description="Battle type: Conquest, Expedition")
    description: str = Field(..., description="Skill description")
    # Internal storage path (excluded from API responses)
    icon_path: str | None = Field(
        default=None,
        description="Storage path for the talent icon inside Supabase Storage",
        exclude=True,
    )

    def apply_defaults(self, hero_id: str) -> None:
        """Populate default icon path when none is provided."""

        if not self.icon_path:
            hero_slug = slugify(hero_id)
            skill_slug = slugify(self.name)
            if hero_slug and skill_slug:
                path = resolve_asset_path(
                    folder=f"skills/{hero_slug}",
                    fallback_name=skill_slug,
                )
                if path:
                    self.icon_path = path

    def model_dump(self, **kwargs) -> dict:  # type: ignore[override]
        """Dump model excluding None values by default."""
        kwargs.setdefault("exclude_none", True)
        return super().model_dump(**kwargs)

    @computed_field
    @property
    def image_url(self) -> str | None:
        """Public URL for the talent icon."""
        return build_public_asset_url(self.icon_path)


class HeroSkillCreate(HeroSkillBase):
    """Model for creating a hero skill."""

    pass


class HeroSkill(HeroSkillBase):
    """Complete hero skill model from database."""

    id: UUID = Field(..., description="Database primary key")
    created_at: Optional[datetime] = None


class HeroSkillLevelBase(BaseModel):
    """Base hero skill level model."""

    model_config = ConfigDict(from_attributes=True)

    skill_id: UUID = Field(..., description="Foreign key to hero_skills table")
    level: int = Field(..., ge=1, le=5, description="Skill level (1-5)")
    effects: Dict[str, Any] = Field(..., description="JSON object with skill effects")


class HeroSkillLevelCreate(HeroSkillLevelBase):
    """Model for creating a hero skill level."""

    pass


class HeroSkillLevel(HeroSkillLevelBase):
    """Complete hero skill level model from database."""

    id: UUID = Field(..., description="Database primary key")
    created_at: Optional[datetime] = None
