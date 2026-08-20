from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings

class Database:
    client: AsyncIOMotorClient = None
    db = None

db = Database()

async def connect_to_mongo():
    db.client = AsyncIOMotorClient(settings.DATABASE_URL)
    db.db = db.client.get_default_database()
    
    # Configure database indexes
    try:
        # Unique index on user email
        await db.db["users"].create_index("email", unique=True)
        # Indexes on predictions for paginated queries
        await db.db["predictions"].create_index([("user_id", 1), ("upload_date", -1)])
        await db.db["predictions"].create_index("filename")
        await db.db["predictions"].create_index("upload_date")
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Failed to initialize database indexes: {e}")

async def close_mongo_connection():
    if db.client:
        db.client.close()

def get_db():
    return db.db
