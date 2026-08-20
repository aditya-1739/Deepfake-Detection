from fastapi import APIRouter
from app.config.settings import settings
import time

router = APIRouter()
START_TIME = time.time()

@router.get("/")
def health_check():
    import torch
    return {
        "success": True,
        "status": "ok",
        "backend": "running",
        "version": settings.APP_VERSION,
        "environment": "development",
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "cuda_available": torch.cuda.is_available(),
        "uptime_seconds": round(time.time() - START_TIME, 2)
    }
