import uuid
from typing import Optional, List
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.postgres.inventory import Warehouse, Inventory, InventoryReservation, InventoryMovement

class InsufficientStockException(Exception):
    def __init__(self, variant_id: uuid.UUID, requested: int, available: int):
        self.variant_id = variant_id
        self.requested = requested
        self.available = available
        super().__init__(f"Insufficient stock for variant {variant_id}. Requested: {requested}, Available: {available}")

class InventoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_warehouse(self, seller_id: uuid.UUID, name: str) -> Warehouse:
        warehouse = Warehouse(seller_id=seller_id, name=name)
        self.session.add(warehouse)
        await self.session.commit()
        await self.session.refresh(warehouse)
        return warehouse

    async def get_warehouse(self, warehouse_id: uuid.UUID) -> Optional[Warehouse]:
        stmt = select(Warehouse).where(Warehouse.id == warehouse_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def adjust_inventory(self, seller_id: uuid.UUID, variant_id: uuid.UUID, warehouse_id: uuid.UUID, quantity: int) -> Inventory:
        # Check if inventory record exists
        stmt = select(Inventory).where(
            and_(
                Inventory.variant_id == variant_id,
                Inventory.warehouse_id == warehouse_id,
                Inventory.seller_id == seller_id
            )
        )
        result = await self.session.execute(stmt)
        inventory = result.scalar_one_or_none()

        if inventory:
            inventory.on_hand += quantity
        else:
            if quantity < 0:
                raise ValueError("Cannot initialize inventory with negative quantity")
            inventory = Inventory(
                variant_id=variant_id,
                warehouse_id=warehouse_id,
                seller_id=seller_id,
                on_hand=quantity,
                reserved=0
            )
            self.session.add(inventory)
            await self.session.flush()

        # Log movement
        movement = InventoryMovement(
            inventory_id=inventory.id,
            quantity_change=quantity,
            reason="MANUAL_ADJUST"
        )
        self.session.add(movement)
        
        await self.session.commit()
        await self.session.refresh(inventory)
        return inventory

    async def reserve_stock(self, variant_id: uuid.UUID, seller_id: uuid.UUID, quantity: int, order_id: uuid.UUID, session: AsyncSession = None) -> InventoryReservation:
        """
        Reserves stock using row-level locking (SELECT ... FOR UPDATE).
        Requires the session to be passed from the order creation transaction so that it rolls back if order creation fails.
        """
        sess = session or self.session

        # Find available inventory for this variant and seller across all their warehouses.
        # Lock the rows using with_for_update() to prevent race conditions.
        stmt = select(Inventory).where(
            and_(
                Inventory.variant_id == variant_id,
                Inventory.seller_id == seller_id
            )
        ).order_by(Inventory.id.asc()).with_for_update()

        result = await sess.execute(stmt)
        inventories = result.scalars().all()

        # We'll try to find a warehouse with enough stock. 
        # For simplicity in S5, we look for one warehouse that has the full quantity.
        selected_inventory = None
        for inv in inventories:
            available = inv.on_hand - inv.reserved
            if available >= quantity:
                selected_inventory = inv
                break
        
        if not selected_inventory:
            # Calculate total available across all warehouses for the error message
            total_available = sum(inv.on_hand - inv.reserved for inv in inventories)
            raise InsufficientStockException(variant_id, quantity, total_available)

        # Reserve
        selected_inventory.reserved += quantity
        
        # Create Reservation Record
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15) # Hold for 15 mins
        reservation = InventoryReservation(
            inventory_id=selected_inventory.id,
            quantity=quantity,
            status="ACTIVE",
            expires_at=expires_at,
            order_id=order_id
        )
        sess.add(reservation)

        # Log movement
        movement = InventoryMovement(
            inventory_id=selected_inventory.id,
            quantity_change=0, # Only reserved changes, on_hand remains
            reason="RESERVE"
        )
        sess.add(movement)

        # We do NOT commit the session here, as it's part of the parent order checkout transaction
        return reservation

    async def commit_reservation(self, order_id: uuid.UUID, session: AsyncSession = None):
        """
        Commits reservations for an order, reducing on_hand and reserved.
        """
        sess = session or self.session
        
        # Find active reservations for order
        stmt = select(InventoryReservation).where(
            and_(
                InventoryReservation.order_id == order_id,
                InventoryReservation.status == "ACTIVE"
            )
        )
        result = await sess.execute(stmt)
        reservations = result.scalars().all()

        for res in reservations:
            res.status = "COMMITTED"
            
            # Fetch and lock inventory
            inv_stmt = select(Inventory).where(Inventory.id == res.inventory_id).with_for_update()
            inv_res = await sess.execute(inv_stmt)
            inventory = inv_res.scalar_one()

            inventory.on_hand -= res.quantity
            inventory.reserved -= res.quantity

            movement = InventoryMovement(
                inventory_id=inventory.id,
                quantity_change=-res.quantity,
                reason="COMMIT"
            )
            sess.add(movement)

    async def release_reservation(self, order_id: uuid.UUID, session: AsyncSession = None):
        """
        Releases reservations for an order (e.g. payment failed), decreasing reserved but leaving on_hand.
        """
        sess = session or self.session
        
        # Find active reservations for order
        stmt = select(InventoryReservation).where(
            and_(
                InventoryReservation.order_id == order_id,
                InventoryReservation.status == "ACTIVE"
            )
        )
        result = await sess.execute(stmt)
        reservations = result.scalars().all()

        for res in reservations:
            res.status = "RELEASED"
            
            # Fetch and lock inventory
            inv_stmt = select(Inventory).where(Inventory.id == res.inventory_id).with_for_update()
            inv_res = await sess.execute(inv_stmt)
            inventory = inv_res.scalar_one()

            inventory.reserved -= res.quantity

            movement = InventoryMovement(
                inventory_id=inventory.id,
                quantity_change=0,
                reason="RELEASE"
            )
            sess.add(movement)
