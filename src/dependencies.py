"""Shared FastAPI dependencies for the KS-Heroes API."""

from fastapi import HTTPException

from supabase import Client

from .db.supabase_client import SupabaseClientError
from .db.supabase_client import get_supabase_client as _get_supabase_client


def get_supabase_client() -> Client:
    """Return the Supabase client instance ready for injection."""

    try:
        client = _get_supabase_client()
    except (
        SupabaseClientError,
        RuntimeError,
    ) as exc:  # pragma: no cover - env specific
        raise HTTPException(
            status_code=503,
            detail="Supabase client is not configured or unavailable.",
        ) from exc

    return client
