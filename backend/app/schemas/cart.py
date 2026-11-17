from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID

class CartItem(BaseModel):
    product_id: UUID
    variant_id: Optional[UUID] = None
    sku: str
    quantity: int
    price_at_add: int
    name: str

class Cart(BaseModel):
    id: str
    items: List[CartItem] = []
    total_price: int = 0

class CartAddRequest(BaseModel):
    product_id: UUID
    variant_id: Optional[UUID] = None
    sku: Optional[str] = None
    quantity: int = 1

class CartUpdateRequest(BaseModel):
    quantity: int
