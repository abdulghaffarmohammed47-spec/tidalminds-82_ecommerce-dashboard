from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from uuid import UUID


class CouponValidationRequest(BaseModel):
    code: str


class CouponValidationResponse(BaseModel):
    id: UUID
    code: str
    discount_type: str
    discount_value: int
    min_order_amount: int
    max_discount_amount: Optional[int] = None
    expires_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)