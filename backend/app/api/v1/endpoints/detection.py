import time
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
MAX_VIDEO_SIZE = 500 * 1024 * 1024  # 500MB

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

@router.post("/image")
async def detect_image(
    file: UploadFile = File(...),
    current_user: Optional[dict] = Depends(get_optional_current_user),
    db=Depends(get_db)
):
    """
    Inference on uploaded face image.
    Accepts: JPG, JPEG, PNG, WEBP.
    """
    logger.info(f"Received image prediction request: {file.filename}")
    
    # 1. Validate file existence and type
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file upload is not allowed."
        )
        
    ext = f".{file.filename.split('.')[-1].lower()}" if "." in file.filename else ""
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported image format '{ext}'. Allowed formats: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
        )
        
    # 2. Validate maximum file size
    await validate_file_size(file, MAX_IMAGE_SIZE)
    
    try:
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty."
            )
            
        # 3. Invoke inference service
        result = inference_service.predict_image(content)
        logger.info(f"Image prediction successful: {result['prediction']} (Confidence: {result['confidence']}%)")
        
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
        logger.warning(f"Decoding failure on image {file.filename}: {ve}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Inference failure on image {file.filename}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal inference failure: {str(e)}"
        )

@router.post("/video")
async def detect_video(
    file: UploadFile = File(...),
    current_user: Optional[dict] = Depends(get_optional_current_user),
    db=Depends(get_db)
):
    """
    Inference on uploaded video.
    Accepts: MP4, AVI, MOV, MKV.
    """
    logger.info(f"Received video prediction request: {file.filename}")
    
    # 1. Validate file existence and type
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file upload is not allowed."
        )
        
    ext = f".{file.filename.split('.')[-1].lower()}" if "." in file.filename else ""
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported video format '{ext}'. Allowed formats: {', '.join(ALLOWED_VIDEO_EXTENSIONS)}"
        )
        
    # 2. Validate maximum file size
    await validate_file_size(file, MAX_VIDEO_SIZE)
    
    try:
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty."
            )
            
        # 3. Invoke inference service
        result = inference_service.predict_video(content)
        logger.info(f"Video prediction successful: {result['prediction']} (Confidence: {result['confidence']}%)")
        
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
        logger.warning(f"Decoding failure on video {file.filename}: {ve}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Inference failure on video {file.filename}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal inference failure: {str(e)}"
        )
