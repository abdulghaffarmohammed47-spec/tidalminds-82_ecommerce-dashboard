import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.schemas.seller import (
    SellerCreate,
    SellerRead,
    SellerMetrics,
    SellerOrderRead,
    SellerOrderStatusUpdate,
    SellerProductCreate,
    SellerProductRead,
    SellerWarehouseRead,
    SellerWarehouseCreate,
    SellerInventoryAdjust,
)
from app.repositories.seller_repository import SellerRepository
from app.repositories.inventory_repository import InventoryRepository
from app.api.dependencies import get_current_user, RoleChecker
from app.models.postgres.auth import User

router = APIRouter(tags=["sellers"])

async def get_current_seller(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    repo = SellerRepository(session)
    seller = await repo.get_seller_by_user_id(current_user.id)
    if not seller:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authenticated user is not registered as a seller"
        )
    return seller

@router.post("/apply", response_model=SellerRead)
async def apply_to_be_seller(
    seller_in: SellerCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    repo = SellerRepository(session)
    existing_seller = await repo.get_seller_by_user_id(current_user.id)
    if existing_seller:
        raise HTTPException(status_code=400, detail="User is already a seller")
    
    seller = await repo.create_seller(current_user.id, seller_in)
    return seller

@router.get("/me", response_model=SellerRead, dependencies=[Depends(RoleChecker(["seller"]))])
async def get_my_seller_profile(
    seller = Depends(get_current_seller)
):
    return seller

@router.get("/me/metrics", response_model=SellerMetrics, dependencies=[Depends(RoleChecker(["seller"]))])
@router.get("/metrics", response_model=SellerMetrics, dependencies=[Depends(RoleChecker(["seller"]))])
async def get_seller_metrics(
    seller = Depends(get_current_seller),
    session: AsyncSession = Depends(get_db)
):
    repo = SellerRepository(session)
    return await repo.get_seller_metrics(seller.id)

@router.get("/me/orders", response_model=List[SellerOrderRead], dependencies=[Depends(RoleChecker(["seller"]))])
@router.get("/orders", response_model=List[SellerOrderRead], dependencies=[Depends(RoleChecker(["seller"]))])
async def get_seller_orders(
    seller = Depends(get_current_seller),
    session: AsyncSession = Depends(get_db)
):
    repo = SellerRepository(session)
    return await repo.get_seller_orders(seller.id)

@router.put("/me/orders/{seller_order_id}/status", response_model=SellerOrderRead, dependencies=[Depends(RoleChecker(["seller"]))])
@router.put("/orders/{seller_order_id}/status", response_model=SellerOrderRead, dependencies=[Depends(RoleChecker(["seller"]))])
async def update_seller_order_status(
    seller_order_id: uuid.UUID,
    req: SellerOrderStatusUpdate,
    seller = Depends(get_current_seller),
    session: AsyncSession = Depends(get_db)
):
    valid_statuses = ["PENDING", "PROCESSING", "SHIPPED", "DELIVERED", "CANCELLED"]
    if req.status.upper() not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status '{req.status}'. Must be one of: {', '.join(valid_statuses)}"
        )
    
    repo = SellerRepository(session)
    updated = await repo.update_seller_order_status(seller.id, seller_order_id, req.status.upper())
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seller order not found or you do not have permission to update it"
        )
    return updated

@router.get("/me/products", response_model=List[SellerProductRead], dependencies=[Depends(RoleChecker(["seller"]))])
@router.get("/products", response_model=List[SellerProductRead], dependencies=[Depends(RoleChecker(["seller"]))])
async def get_seller_products(
    seller = Depends(get_current_seller),
    session: AsyncSession = Depends(get_db)
):
    repo = SellerRepository(session)
    return await repo.get_seller_products(seller.id)

@router.post("/me/products", response_model=SellerProductRead, dependencies=[Depends(RoleChecker(["seller"]))])
@router.post("/products", response_model=SellerProductRead, dependencies=[Depends(RoleChecker(["seller"]))])
async def create_seller_product(
    product_in: SellerProductCreate,
    seller = Depends(get_current_seller),
    session: AsyncSession = Depends(get_db)
):
    repo = SellerRepository(session)
    return await repo.create_seller_product(seller.id, product_in)

@router.get("/me/warehouses", response_model=List[SellerWarehouseRead], dependencies=[Depends(RoleChecker(["seller"]))])
@router.get("/warehouses", response_model=List[SellerWarehouseRead], dependencies=[Depends(RoleChecker(["seller"]))])
async def get_seller_warehouses(
    seller = Depends(get_current_seller),
    session: AsyncSession = Depends(get_db)
):
    repo = SellerRepository(session)
    return await repo.get_seller_warehouses(seller.id)

@router.post("/me/warehouses", response_model=SellerWarehouseRead, dependencies=[Depends(RoleChecker(["seller"]))])
@router.post("/warehouses", response_model=SellerWarehouseRead, dependencies=[Depends(RoleChecker(["seller"]))])
async def create_seller_warehouse(
    req: SellerWarehouseCreate,
    seller = Depends(get_current_seller),
    session: AsyncSession = Depends(get_db)
):
    repo = SellerRepository(session)
    return await repo.create_seller_warehouse(seller.id, req.name)

@router.post("/me/inventory/adjust", dependencies=[Depends(RoleChecker(["seller"]))])
@router.post("/inventory/adjust", dependencies=[Depends(RoleChecker(["seller"]))])
async def adjust_seller_inventory(
    req: SellerInventoryAdjust,
    seller = Depends(get_current_seller),
    session: AsyncSession = Depends(get_db)
):
    inv_repo = InventoryRepository(session)
    try:
        inv = await inv_repo.adjust_inventory(
            seller_id=seller.id,
            variant_id=req.variant_id,
            warehouse_id=req.warehouse_id,
            quantity=req.on_hand
        )
        return {
            "status": "success",
            "variant_id": inv.variant_id,
            "warehouse_id": inv.warehouse_id,
            "on_hand": inv.on_hand,
            "reserved": inv.reserved,
            "available": inv.on_hand - inv.reserved
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
