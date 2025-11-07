from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool

from supabase import Client

from ...dependencies import get_supabase_client
from ...schemas.hero import HeroStatsResponse

router = APIRouter()


@router.get("/conquest", response_model=List[HeroStatsResponse])
async def get_all_conquest_stats(
    supabase: Client = Depends(get_supabase_client),
):
    """
    Retrieve all hero conquest stats.
    """
    query = supabase.table("hero_stats").select("*")
    response = await run_in_threadpool(query.execute)
    if not response.data:
        raise HTTPException(status_code=404, detail="No conquest stats found")
    return response.data
