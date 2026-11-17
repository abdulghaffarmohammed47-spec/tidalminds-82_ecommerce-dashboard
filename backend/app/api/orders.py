from typing import List
from uuid import UUID
import hashlib
import json
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db, get_cart_id
from app.models.postgres.auth import User
from app.repositories.order_repository import OrderRepository
from app.repositories.cart_repository import CartRepository
from app.schemas.order import OrderResponse, OrderCheckoutRequest, SellerOrderStatusUpdateRequest

router = APIRouter()

def get_order_repo(db: AsyncSession = Depends(get_db)) -> OrderRepository:
    return OrderRepository(db)

def get_cart_repo() -> CartRepository:
    return CartRepository()

@router.post("/checkout", response_model=OrderResponse)
async def checkout(
    req: OrderCheckoutRequest = OrderCheckoutRequest(),
    user: User = Depends(get_current_user),
    cart_info: tuple = Depends(get_cart_id),
    order_repo: OrderRepository = Depends(get_order_repo),
    cart_repo: CartRepository = Depends(get_cart_repo),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    cart_id, is_guest = cart_info
    # Fetch user's cart
    cart = await cart_repo.get_cart(cart_id)
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty")

    request_hash = hashlib.sha256(
        json.dumps(req.model_dump(mode="json"), sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    order = await order_repo.create_order(
        user.id,
        cart,
        idempotency_key=idempotency_key,
        request_hash=request_hash,
        coupon_code=req.coupon_code,
    )

    # Clear cart after successful checkout
    await cart_repo.clear_cart(cart_id)

    return order

@router.get("", response_model=List[OrderResponse])
async def get_user_orders(
    user: User = Depends(get_current_user),
    order_repo: OrderRepository = Depends(get_order_repo)
):
    return await order_repo.get_user_orders(user.id)

@router.put("/seller/{order_id}/status")
async def update_seller_order_status(
    order_id: UUID,
    req: SellerOrderStatusUpdateRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    from app.repositories.seller_repository import SellerRepository
    seller_repo = SellerRepository(session)
    seller = await seller_repo.get_seller_by_user_id(user.id)
    if not seller:
        raise HTTPException(status_code=403, detail="User is not registered as a seller")
    
    updated = await seller_repo.update_seller_order_status(seller.id, order_id, req.status)
    if not updated:
        raise HTTPException(status_code=404, detail="Seller order not found or unauthorized")
    return updated

