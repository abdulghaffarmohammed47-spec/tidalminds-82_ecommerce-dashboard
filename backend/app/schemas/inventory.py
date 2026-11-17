from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class WarehouseBase(BaseModel):
    name: str

class WarehouseCreate(WarehouseBase):
    pass

class WarehouseResponse(WarehouseBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    seller_id: UUID

class InventoryBase(BaseModel):
    on_hand: int

class InventoryAdjustRequest(InventoryBase):
    pass

class InventoryResponse(InventoryBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    variant_id: UUID
    warehouse_id: UUID
    seller_id: UUID
    reserved: int
