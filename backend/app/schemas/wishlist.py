from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.catalog import ProductResponse


class WishlistItemCreate(BaseModel):
    product_id: UUID


class WishlistItemResponse(BaseModel):
    id: UUID
    product_id: UUID
    created_at: datetime
    product: ProductResponse

    model_config = ConfigDict(from_attributes=True)