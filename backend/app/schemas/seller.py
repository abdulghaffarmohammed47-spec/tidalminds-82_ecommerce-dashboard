from uuid import UUID
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class SellerCreate(BaseModel):
    company_name: str

class SellerRead(BaseModel):
    id: UUID
    user_id: UUID
    company_name: str
    is_active: bool

    class Config:
        from_attributes = True

class SellerMetrics(BaseModel):
    total_sales: int # in minor units (paise)
    total_sales_display: float
    active_listings: int
    pending_orders: int
    total_orders: int
    low_stock_items: int

class SellerOrderItemRead(BaseModel):
    id: UUID
    variant_id: UUID
    snapshot_name: str
    snapshot_price: int
    quantity: int

    class Config:
        from_attributes = True

class SellerOrderRead(BaseModel):
    id: UUID
    order_id: UUID
    seller_id: UUID
    status: str
    subtotal: int
    created_at: Optional[datetime] = None
    items: List[SellerOrderItemRead] = []

    class Config:
        from_attributes = True

class SellerOrderStatusUpdate(BaseModel):
    status: str # PENDING, PROCESSING, SHIPPED, DELIVERED, CANCELLED

class SellerProductCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    category_id: UUID
    brand_id: UUID
    sku: str
    variant_name: str
    price: int # paise
    attributes: Optional[dict] = {}
    warehouse_id: Optional[UUID] = None
    initial_stock: Optional[int] = 0

class SellerProductRead(BaseModel):
    product_id: UUID
    product_name: str
    category_id: UUID
    brand_id: UUID
    variant_id: UUID
    sku: str
    variant_name: str
    price: int
    is_active: bool
    on_hand: int
    reserved: int
    available: int
    warehouse_id: Optional[UUID] = None
    warehouse_name: Optional[str] = None

class SellerInventoryAdjust(BaseModel):
    variant_id: UUID
    warehouse_id: UUID
    on_hand: int

class SellerWarehouseRead(BaseModel):
    id: UUID
    seller_id: UUID
    name: str

    class Config:
        from_attributes = True

class SellerWarehouseCreate(BaseModel):
    name: str
