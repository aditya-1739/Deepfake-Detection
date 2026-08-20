import logging
import time
import torch
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.api.v1.router import api_router
from app.api.v1.endpoints.predict_alias import router as predict_router
from app.core.exceptions import global_exception_handler

logger = logging.getLogger(__name__)
START_TIME = time.time()

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        openapi_url="/api/v1/openapi.json",
        docs_url="/api/v1/docs",
        redoc_url="/api/v1/redoc",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000", 
            "http://127.0.0.1:3000",
            "https://deepfake-detection-kohl.vercel.app"
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception Handling
    app.add_exception_handler(Exception, global_exception_handler)

    # Include Routes
    app.include_router(api_router, prefix="/api/v1")
    app.include_router(predict_router, prefix="/api", tags=["prediction"])

    # Health and Model Status Endpoints
    @app.get("/api/health", tags=["health"])
    def health_status():
        return {
            "success": True,
            "status": "ok",
            "backend": "running",
            "device": "cuda" if torch.cuda.is_available() else "cpu",
            "cuda_available": torch.cuda.is_available(),
            "uptime_seconds": round(time.time() - START_TIME, 2),
            "version": settings.APP_VERSION
        }

    @app.get("/api/model", tags=["model"])
    def model_status():
        from app.services.inference_service import inference_service
        return {
            "success": True,
            **inference_service.get_status()
        }

    from app.database.connection import connect_to_mongo, close_mongo_connection

    @app.on_event("startup")
    async def startup_event():
        logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}...")
        
        # Connect to MongoDB
        try:
            await connect_to_mongo()
            logger.info("Successfully connected to MongoDB.")
        except Exception as db_err:
            logger.error(f"Failed to connect to MongoDB: {db_err}")
            
        # Initialize and warm up inference model
        try:
            from app.services.inference_service import inference_service
            # Lazy initialize model and execute warmup
            inference_service.warmup()
        except Exception as inference_err:
            logger.error(f"Failed to initialize deepfake inference engine: {inference_err}", exc_info=True)

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Shutting down gracefully...")
        await close_mongo_connection()

    return app

app = create_app()
