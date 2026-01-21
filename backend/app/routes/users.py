from fastapi import APIRouter, Depends
from app.core.auth import get_current_user
from app.db.supabase import supabase

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/init")
def init_user(clerk_user_id: str = Depends(get_current_user)):
    supabase.table("users").upsert(
        {
            "clerk_user_id": clerk_user_id
        },
        on_conflict="clerk_user_id"
    ).execute()

    return {"status": "ok"}
