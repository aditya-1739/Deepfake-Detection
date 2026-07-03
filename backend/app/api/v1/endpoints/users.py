from fastapi import APIRouter, HTTPException, Depends
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/history")
def user_history(current_user: dict = Depends(get_current_user)):
    return {"msg": "History will be returned here", "user": current_user["email"]}
