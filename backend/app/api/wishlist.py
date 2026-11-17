from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.dependencies import get_current_user, get_db
from app.models.postgres.auth import User
from app.models.postgres.catalog import Product
from app.models.postgres.commerce import WishlistItem
from app.schemas.wishlist import WishlistItemCreate, WishlistItemResponse

router = APIRouter()


@router.get("", response_model=list[WishlistItemResponse])
async def list_wishlist(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(WishlistItem)
        .options(selectinload(WishlistItem.product).selectinload(Product.variants))
        .where(WishlistItem.user_id == user.id)
        .order_by(WishlistItem.created_at.desc())
    )
    return list(result.scalars().all())


@router.post("", response_model=WishlistItemResponse, status_code=status.HTTP_201_CREATED)
async def add_to_wishlist(
    payload: WishlistItemCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    product = await db.scalar(select(Product).where(Product.id == payload.product_id, Product.is_active.is_(True)))
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    existing = await db.scalar(
        select(WishlistItem).where(
            WishlistItem.user_id == user.id,
            WishlistItem.product_id == payload.product_id,
        )
    )
    if existing:
        raise HTTPException(status_code=409, detail="Product is already in your wishlist")

    item = WishlistItem(user_id=user.id, product_id=product.id)
    db.add(item)
    await db.commit()
    result = await db.execute(
        select(WishlistItem)
        .options(selectinload(WishlistItem.product).selectinload(Product.variants))
        .where(WishlistItem.id == item.id)
    )
    return result.scalar_one()


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_wishlist(
    product_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        delete(WishlistItem).where(
            WishlistItem.user_id == user.id,
            WishlistItem.product_id == product_id,
        )
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Wishlist item not found")
    await db.commit()