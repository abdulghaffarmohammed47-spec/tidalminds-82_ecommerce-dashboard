from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from typing import Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_cart_id, get_optional_current_user, get_db
from app.repositories.cart_repository import CartRepository
from app.repositories.catalog_repository import CatalogRepository
from app.schemas.cart import Cart, CartAddRequest, CartItem, CartUpdateRequest
from app.models.postgres.auth import User
from app.models.postgres.catalog import SellerOffer

router = APIRouter()

def get_cart_repo() -> CartRepository:
    return CartRepository()

@router.get("", response_model=Cart)
async def get_cart(
    cart_info: Tuple[str, bool] = Depends(get_cart_id),
    repo: CartRepository = Depends(get_cart_repo)
):
    cart_id, _ = cart_info
    return await repo.get_cart(cart_id)

@router.post("/items", response_model=Cart)
async def add_item_to_cart(
    req: CartAddRequest,
    cart_info: Tuple[str, bool] = Depends(get_cart_id),
    repo: CartRepository = Depends(get_cart_repo),
    db: AsyncSession = Depends(get_db)
):
    cart_id, is_guest = cart_info
    catalog_repo = CatalogRepository(db)
    
    product = await catalog_repo.get_product(req.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    variant = None
    if req.variant_id:
        variant = next((v for v in product.variants if v.id == req.variant_id), None)
        if not variant:
            raise HTTPException(status_code=404, detail="Variant not found")
    elif req.sku:
        variant = next((v for v in product.variants if v.sku == req.sku), None)
        if not variant:
            raise HTTPException(status_code=404, detail="Variant not found")
    elif len(product.variants) == 1:
        variant = product.variants[0]
    else:
        raise HTTPException(status_code=400, detail="A product variant is required")

    if req.sku and variant.sku != req.sku:
        raise HTTPException(status_code=400, detail="SKU does not match variant")

    offer_result = await db.execute(
        select(SellerOffer)
        .where(SellerOffer.variant_id == variant.id, SellerOffer.is_active.is_(True))
        .order_by(SellerOffer.price.asc())
        .limit(1)
    )
    offer = offer_result.scalar_one_or_none()
    if not offer:
        raise HTTPException(status_code=409, detail="This product is not currently offered by an active seller")
    
    item = CartItem(
        product_id=req.product_id,
        variant_id=variant.id,
        sku=variant.sku,
        quantity=req.quantity,
        price_at_add=offer.price,
        name=product.name
    )
    
    return await repo.add_item(cart_id, item, is_guest)

@router.put("/items/{sku}", response_model=Cart)
async def update_cart_item(
    sku: str,
    req: CartUpdateRequest,
    cart_info: Tuple[str, bool] = Depends(get_cart_id),
    repo: CartRepository = Depends(get_cart_repo)
):
    cart_id, is_guest = cart_info
    return await repo.update_item_quantity(cart_id, sku, req.quantity, is_guest)

@router.delete("/items/{sku}", response_model=Cart)
async def remove_cart_item(
    sku: str,
    cart_info: Tuple[str, bool] = Depends(get_cart_id),
    repo: CartRepository = Depends(get_cart_repo)
):
    cart_id, is_guest = cart_info
    return await repo.remove_item(cart_id, sku, is_guest)

@router.post("/merge", response_model=Cart)
async def merge_cart(
    guest_session_id: str,
    user: User = Depends(get_optional_current_user),
    repo: CartRepository = Depends(get_cart_repo)
):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Must be logged in to merge carts")
        
    user_cart_id = str(user.id)
    return await repo.merge_carts(guest_session_id, user_cart_id)
