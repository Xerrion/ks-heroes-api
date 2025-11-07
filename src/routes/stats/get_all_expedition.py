from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool

from supabase import Client

from ...dependencies import get_supabase_client
from ...schemas.hero import HeroExpeditionStatsResponse

router = APIRouter()


@router.get("/expedition", response_model=List[HeroExpeditionStatsResponse])
async def get_all_expedition_stats(
    supabase: Client = Depends(get_supabase_client),
):
    """
    Retrieve all hero expedition stats.
    """
    query = supabase.table("hero_expedition_stats").select("*")
    response = await run_in_threadpool(query.execute)
    if not response.data:
        raise HTTPException(status_code=404, detail="No expedition stats found")
    return response.data
