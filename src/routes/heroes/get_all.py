from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool

from supabase import Client

from ...dependencies import get_supabase_client
from ...schemas.hero import HeroBasicResponse

router = APIRouter()


@router.get("/", response_model=List[HeroBasicResponse])
async def get_all_heroes(
    supabase: Client = Depends(get_supabase_client),
):
    """
    Retrieve all heroes with basic information.
    """
    query = supabase.table("heroes").select("*")
    response = await run_in_threadpool(query.execute)
    if not response.data:
        raise HTTPException(status_code=404, detail="No heroes found")
    return response.data
