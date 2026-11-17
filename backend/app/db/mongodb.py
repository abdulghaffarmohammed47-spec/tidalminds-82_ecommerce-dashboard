from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None

db = MongoDB()

def get_mongodb() -> AsyncIOMotorClient:
    return db.client

async def connect_to_mongo():
    db.client = AsyncIOMotorClient(settings.MONGO_URL)
    try:
        await db.client.admin.command("ping")
    except Exception:
        db.client.close()
        db.client = None

async def close_mongo_connection():
    if db.client is not None:
        db.client.close()

def get_database():
    return db.client[settings.MONGO_DB]
