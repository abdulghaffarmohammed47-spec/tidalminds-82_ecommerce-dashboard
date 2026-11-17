from datetime import datetime, timedelta, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db, RoleChecker
from app.api.sellers import get_current_seller
from app.models.postgres.auth import User
from app.models.postgres.commerce import Order, SellerOrder
from app.models.postgres.shipping import Shipment, ShipmentEvent
from app.schemas.shipping import ShipmentResponse

router = APIRouter()

@router.post("/seller-orders/{seller_order_id}", response_model=ShipmentResponse, dependencies=[Depends(RoleChecker(["seller"]))])
async def create_shipment(seller_order_id: UUID, seller=Depends(get_current_seller), db: AsyncSession = Depends(get_db)):
    seller_order = (await db.execute(select(SellerOrder).where(SellerOrder.id == seller_order_id, SellerOrder.seller_id == seller.id))).scalar_one_or_none()
    if not seller_order:
        raise HTTPException(status_code=404, detail="Seller order not found")
    existing = (await db.execute(select(Shipment).where(Shipment.seller_order_id == seller_order_id))).scalar_one_or_none()
    if existing:
        return existing
    shipment = Shipment(
        seller_order_id=seller_order_id,
        provider="MOCK",
        tracking_number=f"MOCK-SCX-{str(seller_order_id).replace('-', '').upper()[:12]}",
        status="LABEL_CREATED",
        estimated_delivery=datetime.now(timezone.utc) + timedelta(days=4),
    )
    seller_order.status = "SHIPPED"
    db.add(shipment)
    db.add(ShipmentEvent(seller_order_id=seller_order_id, status="LABEL_CREATED"))
    await db.commit()
    await db.refresh(shipment)
    return shipment

@router.get("/orders/{order_id}", response_model=list[ShipmentResponse])
async def get_order_shipments(order_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    order = (await db.execute(select(Order).where(Order.id == order_id, Order.user_id == user.id))).scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return list((await db.execute(select(Shipment).join(SellerOrder).where(SellerOrder.order_id == order_id))).scalars().all())