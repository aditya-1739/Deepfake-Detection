import logging
import datetime
from typing import Optional
from fastapi import APIRouter, File, UploadFile, HTTPException, status, Depends
from app.services.inference_service import inference_service
from app.api.deps import get_optional_current_user
from app.database.connection import get_db

logger = logging.getLogger(__name__)
router = APIRouter()

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv"}

MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB

async def validate_file_size(file: UploadFile, max_size: int):
    # Determine file size using seek
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    
    if size > max_size:
        logger.warning(f"File {file.filename} rejected: size {size} bytes exceeds limit of {max_size} bytes.")
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds the limit of {max_size / (1024 * 1024):.0f}MB."
        )

@router.post("/predict/image")
async def predict_image_alias(
    file: UploadFile = File(...),
    current_user: Optional[dict] = Depends(get_optional_current_user),
    db=Depends(get_db)
):
    """
    Direct alias endpoint for image prediction.
    Exposed at: POST /api/predict/image
    """
    logger.info(f"Received predict/image alias request: {file.filename}")
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="Empty file upload is not allowed.")
    ext = f".{file.filename.split('.')[-1].lower()}" if "." in file.filename else ""
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported format '{ext}'.")
        
    await validate_file_size(file, MAX_IMAGE_SIZE)
    
    try:
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        result = inference_service.predict_image(content)
        
        # Save to database if connected
        if db is not None:
            try:
                prediction_doc = {
                    "user_id": current_user["id"] if current_user else None,
                    "filename": file.filename,
                    "prediction": result["prediction"],
                    "confidence": result["confidence"],
                    "processing_time_ms": result["processing_time_ms"],
                    "frames_processed": result["frames_processed"],
                    "device": result["device"],
                    "model_version": result["model_version"],
                    "upload_date": datetime.datetime.now(datetime.timezone.utc)
                }
                await db["predictions"].insert_one(prediction_doc)
            except Exception as db_err:
                logger.error(f"Failed to save image prediction history to database: {db_err}")

        return result
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        logger.error(f"Prediction failure: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict/video")
async def predict_video_alias(
    file: UploadFile = File(...),
    current_user: Optional[dict] = Depends(get_optional_current_user),
    db=Depends(get_db)
):
    """
    Direct alias endpoint for video prediction.
    Exposed at: POST /api/predict/video
    """
    logger.info(f"Received predict/video alias request: {file.filename}")
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="Empty file upload is not allowed.")
    ext = f".{file.filename.split('.')[-1].lower()}" if "." in file.filename else ""
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported format '{ext}'.")
        
    await validate_file_size(file, MAX_VIDEO_SIZE)
    
    try:
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        result = inference_service.predict_video(content)
        
        # Save to database if connected
        if db is not None:
            try:
                prediction_doc = {
                    "user_id": current_user["id"] if current_user else None,
                    "filename": file.filename,
                    "prediction": result["prediction"],
                    "confidence": result["confidence"],
                    "processing_time_ms": result["processing_time_ms"],
                    "frames_processed": result["frames_processed"],
                    "device": result["device"],
                    "model_version": result["model_version"],
                    "upload_date": datetime.datetime.now(datetime.timezone.utc)
                }
                await db["predictions"].insert_one(prediction_doc)
            except Exception as db_err:
                logger.error(f"Failed to save video prediction history to database: {db_err}")

        return result
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        logger.error(f"Prediction failure: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
