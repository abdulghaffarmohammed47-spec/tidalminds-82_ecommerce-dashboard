from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.models.postgres.auth import User
from app.models.postgres.commerce import Coupon
from app.schemas.coupon import CouponValidationRequest, CouponValidationResponse

router = APIRouter()


@router.post("/validate", response_model=CouponValidationResponse)
async def validate_coupon(
    request: CouponValidationRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    coupon = (
        await db.execute(select(Coupon).where(Coupon.code == request.code.strip().upper()))
    ).scalar_one_or_none()
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")
    return coupon