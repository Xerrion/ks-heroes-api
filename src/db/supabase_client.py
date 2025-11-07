"""Factory for the shared Supabase client."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from src.settings import get_supabase_settings


class SupabaseClientError(RuntimeError):
    """Raised when the Supabase client cannot be initialized."""


@lru_cache(maxsize=1)
def get_supabase_client() -> Any:
    """Create and memoize the Supabase client instance.

    Returns:
        Client: The configured Supabase client ready for database access.

    Raises:
        SupabaseClientError: If the client cannot be created.
    """

    settings = get_supabase_settings()
    token = settings.access_token
    if token is None:
        raise SupabaseClientError(
            "Supabase credentials are missing. Provide SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY."
        )

    try:
        from supabase import create_client
    except ImportError as exc:  # pragma: no cover - depends on installation
        raise SupabaseClientError(
            "The 'supabase' package is not installed. Install project dependencies before running the app."
        ) from exc

    try:
        supabase_url = str(settings.url).rstrip("/")
        client = create_client(supabase_url, token)
    except Exception as exc:  # pragma: no cover - network/auth errors
        raise SupabaseClientError(
            "Failed to initialize the Supabase client. Check the configured URL and keys."
        ) from exc

    return client
