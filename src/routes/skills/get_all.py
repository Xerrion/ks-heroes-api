from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool

from src.db.repositories.skills import SkillsRepository
from src.dependencies import get_supabase_client
from src.schemas.hero import HeroSkillResponse
from supabase import Client

router = APIRouter()


@router.get("/", response_model=List[HeroSkillResponse])
async def get_all_skills(
    supabase: Client = Depends(get_supabase_client),
):
    """
    Retrieve all hero skills.
    """
    repository = SkillsRepository(supabase)
    skills = await run_in_threadpool(repository.list_all)
    if not skills:
        raise HTTPException(status_code=404, detail="No skills found")
    return skills
