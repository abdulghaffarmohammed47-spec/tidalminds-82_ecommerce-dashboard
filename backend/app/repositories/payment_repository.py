from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from app.models.postgres.commerce import Order, SellerOrder, OrderStatusHistory
from app.models.postgres.payment import Payment, PaymentAttempt

class PaymentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def simulate_payment(self, order_id: UUID, status: str, user_id: UUID) -> Payment:
        # Serialize payment transitions and enforce customer ownership.
        stmt = select(Order).where(Order.id == order_id).with_for_update()
        result = await self.session.execute(stmt)
        order = result.scalar_one_or_none()

        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        if order.user_id != user_id:
            raise HTTPException(status_code=404, detail="Order not found")
        
        if order.status != "PENDING_PAYMENT":
            raise HTTPException(status_code=400, detail=f"Order is in {order.status} state, cannot process payment")

        # Create Payment record
        payment = Payment(
            order_id=order.id,
            amount=order.total_amount,
            status=status
        )
        self.session.add(payment)
        await self.session.flush()

        # Create PaymentAttempt
        attempt = PaymentAttempt(
            payment_id=payment.id,
            provider_ref="simulated_txn_" + str(payment.id)[:8],
            status=status
        )
        self.session.add(attempt)

        from app.repositories.inventory_repository import InventoryRepository
        inventory_repo = InventoryRepository(self.session)

        # Update Order state
        if status == "SUCCESS":
            order.status = "PAID"
            # Update all seller orders to PROCESSING
            seller_orders_stmt = select(SellerOrder).where(SellerOrder.order_id == order.id)
            seller_orders_res = await self.session.execute(seller_orders_stmt)
            seller_orders = seller_orders_res.scalars().all()
            for so in seller_orders:
                so.status = "PROCESSING"
            
            await inventory_repo.commit_reservation(order.id, self.session)
            
        elif status == "FAILED":
            order.status = "PAYMENT_FAILED"
            await inventory_repo.release_reservation(order.id, self.session)
        else:
            raise HTTPException(status_code=400, detail="Invalid payment status")

        # Add history
        history = OrderStatusHistory(
            order_id=order.id,
            status=order.status
        )
        self.session.add(history)

        await self.session.commit()
        await self.session.refresh(payment)
        return payment
