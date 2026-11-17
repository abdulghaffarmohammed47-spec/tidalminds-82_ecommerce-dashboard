from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

class PaymentSimulationRequest(BaseModel):
    status: str # e.g. "SUCCESS", "FAILED"

class PaymentResponse(BaseModel):
    id: UUID
    order_id: UUID
    amount: int
    status: str
    
    model_config = ConfigDict(from_attributes=True)
