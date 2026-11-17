import hashlib
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from app.models.postgres.commerce import Order, SellerOrder, OrderItem, OrderStatusHistory, Coupon, CouponRedemption
from app.models.postgres.catalog import SellerOffer, ProductVariant
from app.models.postgres.system import IdempotencyKey, OutboxEvent
from app.schemas.cart import Cart

class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_order(
        self,
        user_id: UUID,
        cart: Cart,
        idempotency_key: Optional[str] = None,
        request_hash: Optional[str] = None,
        coupon_code: Optional[str] = None,
    ) -> Order:
        endpoint = "POST:/api/orders/checkout"
        if idempotency_key:
            if not request_hash:
                request_hash = hashlib.sha256(b"{}").hexdigest()

            # ON CONFLICT makes simultaneous retries converge on one key row.
            await self.session.execute(
                insert(IdempotencyKey)
                .values(
                    user_id=user_id,
                    endpoint=endpoint,
                    key=idempotency_key,
                    request_hash=request_hash,
                )
                .on_conflict_do_nothing(
                    index_elements=[IdempotencyKey.user_id, IdempotencyKey.endpoint, IdempotencyKey.key]
                )
            )
            key_result = await self.session.execute(
                select(IdempotencyKey)
                .where(
                    IdempotencyKey.user_id == user_id,
                    IdempotencyKey.endpoint == endpoint,
                    IdempotencyKey.key == idempotency_key,
                )
                .with_for_update()
            )
            stored_key = key_result.scalar_one()
            if stored_key.request_hash != request_hash:
                raise HTTPException(status_code=409, detail="Idempotency key was reused with a different request")
            if stored_key.response_body and stored_key.response_body.get("order_id"):
                return await self.get_order(UUID(stored_key.response_body["order_id"]))

        if not cart.items:
            raise HTTPException(status_code=400, detail="Cart is empty")

        total_amount = 0
        seller_subtotals: Dict[UUID, int] = {}
        seller_items: Dict[UUID, List[Dict[str, Any]]] = {}

        for item in cart.items:
            if not item.variant_id:
                raise HTTPException(status_code=400, detail=f"Variant ID missing for SKU {item.sku}")
                
            # Find cheapest active SellerOffer for this variant
            stmt = select(SellerOffer).where(
                SellerOffer.variant_id == item.variant_id,
                SellerOffer.is_active == True
            ).order_by(SellerOffer.price.asc()).limit(1)
            
            result = await self.session.execute(stmt)
            offer = result.scalar_one_or_none()
            
            if not offer:
                raise HTTPException(status_code=400, detail=f"No active offers for variant {item.variant_id}")

            seller_id = offer.seller_id
            price = offer.price
            subtotal = price * item.quantity
            
            total_amount += subtotal
            seller_subtotals[seller_id] = seller_subtotals.get(seller_id, 0) + subtotal
            
            if seller_id not in seller_items:
                seller_items[seller_id] = []
                
            seller_items[seller_id].append({
                "variant_id": item.variant_id,
                "snapshot_price": price,
                "snapshot_name": item.name,
                "quantity": item.quantity
            })

        discount_amount = 0
        coupon = None

        if coupon_code:
            coupon = (
                await self.session.execute(
                    select(Coupon).where(Coupon.code == coupon_code.strip().upper()).with_for_update()
                )
            ).scalar_one_or_none()
            if not coupon:
                raise HTTPException(status_code=400, detail="Coupon not found")
            if coupon.expires_at and coupon.expires_at <= datetime.now(timezone.utc):
                raise HTTPException(status_code=400, detail="Coupon has expired")
            if coupon.min_order_amount > total_amount:
                raise HTTPException(status_code=400, detail="Order does not meet the coupon minimum")
            total_redemptions = await self.session.scalar(
                select(func.count(CouponRedemption.id)).where(CouponRedemption.coupon_id == coupon.id)
            )
            user_redemptions = await self.session.scalar(
                select(func.count(CouponRedemption.id)).where(
                    CouponRedemption.coupon_id == coupon.id,
                    CouponRedemption.user_id == user_id,
                )
            )
            if coupon.usage_limit > 0 and total_redemptions >= coupon.usage_limit:
                raise HTTPException(status_code=400, detail="Coupon usage limit reached")
            if coupon.per_user_limit > 0 and user_redemptions >= coupon.per_user_limit:
                raise HTTPException(status_code=400, detail="Coupon per-user limit reached")
            if coupon.discount_type == "PERCENTAGE":
                discount_amount = total_amount * coupon.discount_value // 100
            elif coupon.discount_type == "FIXED":
                discount_amount = coupon.discount_value
            else:
                raise HTTPException(status_code=400, detail="Unsupported coupon type")
            if coupon.max_discount_amount is not None:
                discount_amount = min(discount_amount, coupon.max_discount_amount)
            discount_amount = min(discount_amount, total_amount)

        total_amount -= discount_amount

        # Create Order
        order = Order(
            user_id=user_id,
            status="PENDING_PAYMENT",
            total_amount=total_amount,
            currency="INR"
        )
        self.session.add(order)
        await self.session.flush() # get order.id

        if coupon:
            self.session.add(CouponRedemption(coupon_id=coupon.id, user_id=user_id, order_id=order.id))

        # Add OrderStatusHistory
        history = OrderStatusHistory(
            order_id=order.id,
            status="PENDING_PAYMENT"
        )
        self.session.add(history)

        from app.repositories.inventory_repository import InventoryRepository, InsufficientStockException
        inventory_repo = InventoryRepository(self.session)

        # Create SellerOrders and OrderItems
        for seller_id, items in seller_items.items():
            seller_order = SellerOrder(
                order_id=order.id,
                seller_id=seller_id,
                status="PENDING",
                subtotal=seller_subtotals[seller_id]
            )
            self.session.add(seller_order)
            await self.session.flush()
            
            for item_data in items:
                order_item = OrderItem(
                    seller_order_id=seller_order.id,
                    variant_id=item_data["variant_id"],
                    snapshot_price=item_data["snapshot_price"],
                    snapshot_name=item_data["snapshot_name"],
                    quantity=item_data["quantity"]
                )
                self.session.add(order_item)

        # Enforce deterministic global lock order across all items (Deadlock Prevention: TC-35)
        all_reservations = []
        for seller_id, items in seller_items.items():
            for item_data in items:
                all_reservations.append((seller_id, item_data))
        all_reservations.sort(key=lambda x: str(x[1]["variant_id"]))

        for seller_id, item_data in all_reservations:
            try:
                await inventory_repo.reserve_stock(
                    variant_id=item_data["variant_id"],
                    seller_id=seller_id,
                    quantity=item_data["quantity"],
                    order_id=order.id,
                    session=self.session
                )
            except InsufficientStockException as e:
                # Make the failed transaction reusable if the caller handles the error.
                await self.session.rollback()
                raise HTTPException(status_code=400, detail=str(e)) from e

        if idempotency_key:
            stored_key.response_body = {"order_id": str(order.id)}

        self.session.add(
            OutboxEvent(
                topic="OrderCreated",
                payload={
                    "order_id": str(order.id),
                    "user_id": str(user_id),
                    "total_amount": total_amount,
                },
            )
        )

        await self.session.commit()
        await self.session.refresh(order)
        return await self.get_order(order.id)

    async def get_order(self, order_id: UUID) -> Order:
        stmt = select(Order).options(
            selectinload(Order.seller_orders).selectinload(SellerOrder.items)
        ).where(Order.id == order_id)
        
        result = await self.session.execute(stmt)
        order = result.scalar_one_or_none()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order

    async def get_user_orders(self, user_id: UUID) -> List[Order]:
        stmt = select(Order).options(
            selectinload(Order.seller_orders).selectinload(SellerOrder.items)
        ).where(Order.user_id == user_id).order_by(Order.created_at.desc())
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_seller_order_status(self, seller_order_id: UUID, seller_id: UUID, status: str) -> SellerOrder:
        stmt = select(SellerOrder).where(
            SellerOrder.id == seller_order_id,
            SellerOrder.seller_id == seller_id
        )
        result = await self.session.execute(stmt)
        seller_order = result.scalar_one_or_none()
        
        if not seller_order:
            raise HTTPException(status_code=404, detail="Seller order not found or unauthorized")
            
        seller_order.status = status
        await self.session.commit()
        await self.session.refresh(seller_order)
        return seller_order
