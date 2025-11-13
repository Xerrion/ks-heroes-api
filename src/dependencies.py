"""Shared FastAPI dependencies for the KS-Heroes API."""

from fastapi import Depends, HTTPException

from supabase import Client

from .db.repositories.troops import TroopsRepository
from .db.repositories.vip import VIPRepository
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


def get_vip_repository(
    supabase: Client = Depends(get_supabase_client),
) -> VIPRepository:
    """Dependency injection for VIP repository."""
    return VIPRepository(supabase)


def get_troops_repository(
    supabase: Client = Depends(get_supabase_client),
) -> TroopsRepository:
    """Dependency injection for Troops repository."""
    return TroopsRepository(supabase)
