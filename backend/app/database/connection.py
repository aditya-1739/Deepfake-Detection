from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings

class Database:
    client: AsyncIOMotorClient = None
    db = None

db = Database()

async def connect_to_mongo():
    db.client = AsyncIOMotorClient(settings.DATABASE_URL)
    db.db = db.client.get_default_database()

async def close_mongo_connection():
    if db.client:
        db.client.close()

def get_db():
    return db.db
