import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.api.v1.router import api_router
from app.core.exceptions import global_exception_handler

logger = logging.getLogger(__name__)

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
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception Handling
    app.add_exception_handler(Exception, global_exception_handler)

    # Include Routes
    app.include_router(api_router, prefix="/api/v1")

    from app.database.connection import connect_to_mongo, close_mongo_connection

    @app.on_event("startup")
    async def startup_event():
        logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}...")
        await connect_to_mongo()

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Shutting down gracefully...")
        await close_mongo_connection()

    return app

app = create_app()
