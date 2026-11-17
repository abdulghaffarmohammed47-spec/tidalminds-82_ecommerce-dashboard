from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.models.postgres.auth import User
from app.repositories.payment_repository import PaymentRepository
from app.schemas.payment import PaymentResponse, PaymentSimulationRequest

router = APIRouter()

def get_payment_repo(db: AsyncSession = Depends(get_db)) -> PaymentRepository:
    return PaymentRepository(db)

@router.post("/{order_id}/simulate", response_model=PaymentResponse)
async def simulate_payment(
    order_id: UUID,
    req: PaymentSimulationRequest,
    user: User = Depends(get_current_user),
    payment_repo: PaymentRepository = Depends(get_payment_repo)
):
    # Simulates a payment webhook or synchronous response
    if req.status not in ["SUCCESS", "FAILED"]:
        raise HTTPException(status_code=400, detail="Invalid simulation status")

    return await payment_repo.simulate_payment(order_id, req.status, user.id)
