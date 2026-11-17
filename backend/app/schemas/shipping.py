from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class ShipmentResponse(BaseModel):
    id: UUID
    seller_order_id: UUID
    provider: str
    tracking_number: str
    status: str
    estimated_delivery: datetime | None = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)