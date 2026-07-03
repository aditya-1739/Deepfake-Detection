from fastapi import APIRouter
from app.config.settings import settings
import time

router = APIRouter()
START_TIME = time.time()

@router.get("/")
def health_check():
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
        "environment": "development",
        "uptime": time.time() - START_TIME,
        "backend": "running"
    }
