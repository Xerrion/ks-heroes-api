"""Supabase configuration helpers."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv
from pydantic import (
    AnyUrl,
    BaseModel,
    ConfigDict,
    ValidationError,
    field_validator,
    model_validator,
)

# Load environment variables from a local .env file if present.
load_dotenv()


class SupabaseSettings(BaseModel):
    """Container for Supabase connection configuration (no auth layer)."""

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    url: AnyUrl
    service_role_key: Optional[str] = None
    anon_key: Optional[str] = None

    @field_validator("service_role_key", "anon_key", mode="before")
    @classmethod
    def _normalize_empty_strings(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    @model_validator(mode="after")
    def _ensure_credentials(self) -> "SupabaseSettings":
        if not (self.service_role_key or self.anon_key):
            raise ValueError(
                "Provide SUPABASE_ANON_KEY (or SUPABASE_SERVICE_ROLE_KEY) so the application can connect to Supabase."
            )
        return self

    @property
    def access_token(self) -> Optional[str]:
        """Return the most privileged available key for the Supabase client."""
        return self.service_role_key or self.anon_key


@lru_cache(maxsize=1)
def get_supabase_settings() -> SupabaseSettings:
    """Read Supabase connection settings from the environment."""

    url = os.getenv("SUPABASE_URL")
    if not url:
        raise RuntimeError(
            "SUPABASE_URL is not set. Update your environment or .env file before continuing."
        )

    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    anon_key = os.getenv("SUPABASE_ANON_KEY")
    try:
        return SupabaseSettings.model_validate(
            {
                "url": url,
                "service_role_key": service_role_key,
                "anon_key": anon_key,
            }
        )
    except ValidationError as exc:
        first_error = exc.errors()[0] if exc.errors() else {}
        message = first_error.get("msg", str(exc))
        raise RuntimeError(message) from exc
