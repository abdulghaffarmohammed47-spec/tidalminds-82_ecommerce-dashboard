from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime

class OrderItemResponse(BaseModel):
    id: UUID
    seller_order_id: UUID
    variant_id: UUID
    snapshot_price: int
    snapshot_name: str
    quantity: int
    
    model_config = ConfigDict(from_attributes=True)

class SellerOrderResponse(BaseModel):
    id: UUID
    order_id: UUID
    seller_id: UUID
    status: str
    subtotal: int
    items: List[OrderItemResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

class OrderResponse(BaseModel):
    id: UUID
    user_id: UUID
    status: str
    total_amount: int
    currency: str
    created_at: datetime
    seller_orders: List[SellerOrderResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

class OrderCheckoutRequest(BaseModel):
    coupon_code: Optional[str] = None

class SellerOrderStatusUpdateRequest(BaseModel):
    status: str
