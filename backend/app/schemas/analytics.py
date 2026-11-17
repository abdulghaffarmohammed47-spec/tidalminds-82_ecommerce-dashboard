from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import uuid

class AnalyticsEventCreate(BaseModel):
    event_type: str = Field(..., description="E.g., view_product, add_to_cart, checkout")
    product_id: Optional[uuid.UUID] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AnalyticsEvent(AnalyticsEventCreate):
    id: str
    user_id: Optional[uuid.UUID] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProductRecommendation(BaseModel):
    product_id: uuid.UUID
    score: float
