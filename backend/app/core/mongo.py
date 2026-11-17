from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client = AsyncIOMotorClient(settings.MONGO_URL)
db = client[settings.MONGO_DB]

def get_mongo_db():
    return db

async def init_mongo_indexes():
    """Ensure indexes for rich media and specifications in MongoDB"""
    try:
        await db.product_multimedia.create_index("product_id", unique=True)
        await db.product_multimedia.create_index("sku")
    except Exception as e:
        print(f"Warning: Failed to create mongo index: {e}")
