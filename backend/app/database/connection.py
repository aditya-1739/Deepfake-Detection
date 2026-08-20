from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings

class Database:
    client: AsyncIOMotorClient = None
    db = None

db = Database()

async def connect_to_mongo():
    import logging
    logger = logging.getLogger(__name__)
    
    # Use a short timeout so we don't block startup if MongoDB is missing
    db.client = AsyncIOMotorClient(settings.DATABASE_URL, serverSelectionTimeoutMS=2000)
    
    try:
        # Verify connection before proceeding
        await db.client.admin.command('ping')
        db.db = db.client.get_default_database()
        
        # Configure database indexes
        await db.db["users"].create_index("email", unique=True)
        await db.db["predictions"].create_index([("user_id", 1), ("upload_date", -1)])
        await db.db["predictions"].create_index("filename")
        await db.db["predictions"].create_index("upload_date")
    except Exception as e:
        logger.warning(f"MongoDB is unavailable ({e}). Continuing without database support.")
        db.client = None
        db.db = None

async def close_mongo_connection():
    if db.client:
        db.client.close()

def get_db():
    return db.db
