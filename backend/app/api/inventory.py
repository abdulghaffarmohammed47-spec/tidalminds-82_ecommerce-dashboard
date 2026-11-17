import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.models.postgres.auth import User
from app.api.dependencies import get_current_user
from app.schemas.inventory import WarehouseCreate, WarehouseResponse, InventoryAdjustRequest, InventoryResponse
from app.repositories.inventory_repository import InventoryRepository

router = APIRouter(tags=["inventory"])

def get_inventory_repo(db: AsyncSession = Depends(get_db)) -> InventoryRepository:
    return InventoryRepository(db)

@router.post("/warehouses", response_model=WarehouseResponse)
async def create_warehouse(
    req: WarehouseCreate,
    user: User = Depends(get_current_user),
    repo: InventoryRepository = Depends(get_inventory_repo),
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy import select
    from app.models.postgres.catalog import Seller
    stmt = select(Seller).where(Seller.user_id == user.id)
    res = await db.execute(stmt)
    seller = res.scalar_one_or_none()
    if not seller:
        raise HTTPException(status_code=403, detail="User is not a registered seller")

    warehouse = await repo.create_warehouse(seller.id, req.name)
    return warehouse

@router.post("/{variant_id}/warehouses/{warehouse_id}/adjust", response_model=InventoryResponse)
async def adjust_inventory(
    variant_id: uuid.UUID,
    warehouse_id: uuid.UUID,
    req: InventoryAdjustRequest,
    user: User = Depends(get_current_user),
    repo: InventoryRepository = Depends(get_inventory_repo),
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy import select
    from app.models.postgres.catalog import Seller
    stmt = select(Seller).where(Seller.user_id == user.id)
    res = await db.execute(stmt)
    seller = res.scalar_one_or_none()
    if not seller:
        raise HTTPException(status_code=403, detail="User is not a registered seller")

    try:
        inventory = await repo.adjust_inventory(
            seller_id=seller.id,
            variant_id=variant_id,
            warehouse_id=warehouse_id,
            quantity=req.on_hand
        )
        return inventory
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{warehouse_id}", response_model=WarehouseResponse)
async def get_warehouse(
    warehouse_id: uuid.UUID,
    repo: InventoryRepository = Depends(get_inventory_repo)
):
    warehouse = await repo.get_warehouse(warehouse_id)
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return warehouse
