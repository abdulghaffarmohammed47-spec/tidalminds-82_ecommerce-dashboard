from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

class ReturnCreateRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=500)

class ReturnStatusRequest(BaseModel):
    status: str

class ReturnResponse(BaseModel):
    id: UUID
    seller_order_id: UUID
    status: str
    reason: str | None = None
    model_config = ConfigDict(from_attributes=True)