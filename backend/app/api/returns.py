from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db, RoleChecker
from app.api.sellers import get_current_seller
from app.models.postgres.auth import User
from app.models.postgres.commerce import Order, SellerOrder, OrderItem
from app.models.postgres.payment import Payment, Refund
from app.models.postgres.shipping import Return, ReturnItem
from app.models.postgres.inventory import Inventory, InventoryMovement
from app.schemas.returns import ReturnCreateRequest, ReturnStatusRequest, ReturnResponse

router = APIRouter()

@router.post("/seller-orders/{seller_order_id}", response_model=ReturnResponse)
async def request_return(
    seller_order_id: UUID,
    request: ReturnCreateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    seller_order = (
        await db.execute(
            select(SellerOrder).join(Order).where(SellerOrder.id == seller_order_id, Order.user_id == user.id)
        )
    ).scalar_one_or_none()
    if not seller_order:
        raise HTTPException(status_code=404, detail="Seller order not found")
    existing = (await db.execute(select(Return).where(Return.seller_order_id == seller_order_id))).scalar_one_or_none()
    if existing:
        return existing
    if seller_order.status not in {"DELIVERED", "SHIPPED"}:
        raise HTTPException(status_code=400, detail="Only shipped or delivered orders can be returned")
    result = await db.execute(select(OrderItem).where(OrderItem.seller_order_id == seller_order_id))
    order_items = list(result.scalars().all())
    return_record = Return(seller_order_id=seller_order_id, status="REQUESTED", reason=request.reason)
    db.add(return_record)
    await db.flush()
    for item in order_items:
        db.add(ReturnItem(return_id=return_record.id, order_item_id=item.id, quantity=item.quantity))
    seller_order.status = "RETURN_REQUESTED"
    await db.commit()
    await db.refresh(return_record)
    return return_record

@router.get("/orders/{order_id}", response_model=list[ReturnResponse])
async def get_order_returns(order_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    owned = (await db.execute(select(Order.id).where(Order.id == order_id, Order.user_id == user.id))).scalar_one_or_none()
    if not owned:
        raise HTTPException(status_code=404, detail="Order not found")
    return list((await db.execute(select(Return).join(SellerOrder).where(SellerOrder.order_id == order_id))).scalars().all())

@router.put("/{return_id}/status", response_model=ReturnResponse, dependencies=[Depends(RoleChecker(["seller"]))])
async def update_return_status(
    return_id: UUID,
    request: ReturnStatusRequest,
    seller=Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    record = (
        await db.execute(
            select(Return).join(SellerOrder).where(Return.id == return_id, SellerOrder.seller_id == seller.id).with_for_update()
        )
    ).scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Return not found")
    if record.status not in {"REQUESTED", "APPROVED"}:
        raise HTTPException(status_code=400, detail=f"Return is already {record.status}")
    if request.status not in {"APPROVED", "REJECTED"}:
        raise HTTPException(status_code=400, detail="Status must be APPROVED or REJECTED")
    seller_order = (await db.execute(select(SellerOrder).where(SellerOrder.id == record.seller_order_id))).scalar_one()
    if request.status == "REJECTED":
        record.status = "REJECTED"
    else:
        payment = (await db.execute(select(Payment).join(Order).where(Order.id == seller_order.order_id).with_for_update())).scalar_one_or_none()
        if not payment or payment.status != "SUCCESS":
            raise HTTPException(status_code=400, detail="A successful payment is required for refund")
        existing_refund = (await db.execute(select(Refund).where(Refund.payment_id == payment.id))).scalar_one_or_none()
        if existing_refund:
            record.status = "REFUNDED" if existing_refund.status == "SUCCESS" else record.status
        else:
            amount = seller_order.subtotal
            db.add(Refund(payment_id=payment.id, amount=amount, status="SUCCESS"))
            payment.status = "REFUNDED"
            record.status = "REFUNDED"
            seller_order.status = "REFUNDED"
            items = list((await db.execute(select(OrderItem).where(OrderItem.seller_order_id == seller_order.id))).scalars().all())
            for item in items:
                inventory = (await db.execute(select(Inventory).where(Inventory.variant_id == item.variant_id, Inventory.seller_id == seller.id).order_by(Inventory.id).with_for_update())).scalars().first()
                if inventory:
                    inventory.on_hand += item.quantity
                    db.add(InventoryMovement(inventory_id=inventory.id, quantity_change=item.quantity, reason="RETURN"))
    await db.commit()
    await db.refresh(record)
    return record