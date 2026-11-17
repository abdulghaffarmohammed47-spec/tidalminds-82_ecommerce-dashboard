import uuid
from typing import List
from datetime import datetime, timezone, timedelta
from app.db.mongodb import get_database
from app.schemas.analytics import AnalyticsEventCreate, ProductRecommendation

class AnalyticsService:
    def __init__(self):
        # Using a property or calling get_database() when needed is safer for Motor 
        # since it might not be initialized at import time.
        pass

    @property
    def collection(self):
        db = get_database()
        return db["analytics_events"]

    async def log_event(self, event_data: AnalyticsEventCreate, user_id: uuid.UUID = None):
        """Log a user interaction event to MongoDB."""
        doc = event_data.model_dump()
        doc["timestamp"] = datetime.now(timezone.utc)
        if user_id:
            doc["user_id"] = str(user_id)
        if doc.get("product_id"):
            doc["product_id"] = str(doc["product_id"])
        
        await self.collection.insert_one(doc)
        return True

    async def get_trending_products(self, limit: int = 5) -> List[ProductRecommendation]:
        """
        Find most viewed/interacted products in the last 24 hours.
        """
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        
        pipeline = [
            {"$match": {"timestamp": {"$gte": yesterday}, "product_id": {"$exists": True, "$ne": None}}},
            {"$group": {"_id": "$product_id", "score": {"$sum": 1}}},
            {"$sort": {"score": -1}},
            {"$limit": limit}
        ]
        
        cursor = self.collection.aggregate(pipeline)
        results = await cursor.to_list(length=limit)
        
        return [
            ProductRecommendation(product_id=uuid.UUID(r["_id"]), score=r["score"])
            for r in results
        ]

    async def get_recommendations_for_product(self, product_id: uuid.UUID, limit: int = 5) -> List[ProductRecommendation]:
        """
        Simple Item-to-Item Collaborative Filtering via Aggregation.
        "Users who viewed this product also viewed..."
        """
        product_id_str = str(product_id)
        
        # 1. Find all users (or sessions) who interacted with THIS product
        users_cursor = self.collection.find({"product_id": product_id_str}, {"user_id": 1, "session_id": 1})
        users_list = await users_cursor.to_list(length=1000)
        
        user_ids = [u["user_id"] for u in users_list if u.get("user_id")]
        session_ids = [u["session_id"] for u in users_list if u.get("session_id")]
        
        if not user_ids and not session_ids:
            return []
            
        # 2. Find other products interacted by these users/sessions, excluding the target product
        match_conds = []
        if user_ids:
            match_conds.append({"user_id": {"$in": user_ids}})
        if session_ids:
            match_conds.append({"session_id": {"$in": session_ids}})
            
        pipeline = [
            {
                "$match": {
                    "$or": match_conds,
                    "product_id": {"$ne": product_id_str, "$exists": True, "$ne": None}
                }
            },
            {"$group": {"_id": "$product_id", "score": {"$sum": 1}}},
            {"$sort": {"score": -1}},
            {"$limit": limit}
        ]
        
        cursor = self.collection.aggregate(pipeline)
        results = await cursor.to_list(length=limit)
        
        return [
            ProductRecommendation(product_id=uuid.UUID(r["_id"]), score=r["score"])
            for r in results
        ]
