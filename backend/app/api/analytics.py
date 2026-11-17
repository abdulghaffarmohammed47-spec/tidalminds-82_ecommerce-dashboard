import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from app.api.dependencies import get_current_user
from app.models.postgres.auth import User
from app.schemas.analytics import AnalyticsEventCreate, ProductRecommendation
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])

class EventResponse(BaseModel):
    success: bool

@router.post("/event", response_model=EventResponse)
async def log_event(
    event_data: AnalyticsEventCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Log an analytics event.
    In a real system, you might allow unauthenticated sessions to log events too.
    """
    service = AnalyticsService()
    await service.log_event(event_data, user_id=current_user.id)
    return EventResponse(success=True)

@router.get("/trending", response_model=List[ProductRecommendation])
async def get_trending_products():
    """Get most interacted products in the last 24h."""
    service = AnalyticsService()
    return await service.get_trending_products()

@router.get("/recommendations/{product_id}", response_model=List[ProductRecommendation])
async def get_recommendations(product_id: uuid.UUID):
    """Get product recommendations based on item-to-item collaborative filtering."""
    service = AnalyticsService()
    return await service.get_recommendations_for_product(product_id)
