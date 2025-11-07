from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool

from supabase import Client

from ...dependencies import get_supabase_client
from ...schemas.hero import HeroSkillResponse

router = APIRouter()


@router.get("/", response_model=List[HeroSkillResponse])
async def get_all_skills(
    supabase: Client = Depends(get_supabase_client),
):
    """
    Retrieve all hero skills.
    """
    query = supabase.table("hero_skills").select("*")
    response = await run_in_threadpool(query.execute)
    if not response.data:
        raise HTTPException(status_code=404, detail="No skills found")
    return response.data
