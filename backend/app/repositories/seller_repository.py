import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.models.postgres.catalog import Seller, SellerOffer, Product, ProductVariant, Category, Brand
from app.models.postgres.inventory import Warehouse, Inventory, InventoryMovement
from app.models.postgres.commerce import SellerOrder, OrderItem, Order
from app.schemas.seller import (
    SellerCreate,
    SellerMetrics,
    SellerOrderRead,
    SellerOrderItemRead,
    SellerProductCreate,
    SellerProductRead,
    SellerWarehouseRead,
)
from app.repositories.user_repository import UserRepository
from app.services.search import SearchService

class SellerRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_seller_by_user_id(self, user_id: uuid.UUID | str) -> Optional[Seller]:
        stmt = select(Seller).where(Seller.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_seller_by_id(self, seller_id: uuid.UUID) -> Optional[Seller]:
        stmt = select(Seller).where(Seller.id == seller_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def create_seller(self, user_id: uuid.UUID | str, seller_create: SellerCreate) -> Seller:
        db_seller = Seller(user_id=user_id, company_name=seller_create.company_name)
        self.session.add(db_seller)
        await self.session.flush()

        # Add seller role to user
        user_repo = UserRepository(self.session)
        await user_repo.assign_role(user_id, "seller")

        # Automatically provision a default warehouse for the seller
        default_wh = Warehouse(seller_id=db_seller.id, name=f"{seller_create.company_name} Primary Hub")
        self.session.add(default_wh)

        await self.session.commit()
        await self.session.refresh(db_seller)
        return db_seller

    async def get_seller_metrics(self, seller_id: uuid.UUID) -> SellerMetrics:
        # Total sales from seller orders (excluding CANCELLED)
        sales_stmt = select(func.coalesce(func.sum(SellerOrder.subtotal), 0)).where(
            SellerOrder.seller_id == seller_id,
            SellerOrder.status != "CANCELLED"
        )
        total_sales_res = await self.session.execute(sales_stmt)
        total_sales = total_sales_res.scalar() or 0

        # Active listings count
        active_stmt = select(func.count(SellerOffer.id)).where(
            SellerOffer.seller_id == seller_id,
            SellerOffer.is_active == True
        )
        active_res = await self.session.execute(active_stmt)
        active_listings = active_res.scalar() or 0

        # Pending orders count (PENDING or PROCESSING)
        pending_stmt = select(func.count(SellerOrder.id)).where(
            SellerOrder.seller_id == seller_id,
            SellerOrder.status.in_(["PENDING", "PROCESSING"])
        )
        pending_res = await self.session.execute(pending_stmt)
        pending_orders = pending_res.scalar() or 0

        # Total orders count
        total_orders_stmt = select(func.count(SellerOrder.id)).where(
            SellerOrder.seller_id == seller_id
        )
        total_orders_res = await self.session.execute(total_orders_stmt)
        total_orders = total_orders_res.scalar() or 0

        # Low stock items count (available < 10)
        low_stock_stmt = select(func.count(Inventory.id)).where(
            Inventory.seller_id == seller_id,
            (Inventory.on_hand - Inventory.reserved) < 10
        )
        low_stock_res = await self.session.execute(low_stock_stmt)
        low_stock_items = low_stock_res.scalar() or 0

        return SellerMetrics(
            total_sales=total_sales,
            total_sales_display=round(total_sales / 100.0, 2),
            active_listings=active_listings,
            pending_orders=pending_orders,
            total_orders=total_orders,
            low_stock_items=low_stock_items
        )

    async def get_seller_orders(self, seller_id: uuid.UUID) -> List[SellerOrderRead]:
        stmt = (
            select(SellerOrder)
            .options(
                selectinload(SellerOrder.items),
                selectinload(SellerOrder.order)
            )
            .where(SellerOrder.seller_id == seller_id)
            .order_by(SellerOrder.id.desc())
        )
        result = await self.session.execute(stmt)
        orders = result.scalars().all()

        output = []
        for so in orders:
            items = [
                SellerOrderItemRead(
                    id=item.id,
                    variant_id=item.variant_id,
                    snapshot_name=item.snapshot_name,
                    snapshot_price=item.snapshot_price,
                    quantity=item.quantity
                )
                for item in so.items
            ]
            created_at = so.order.created_at if so.order else None
            output.append(
                SellerOrderRead(
                    id=so.id,
                    order_id=so.order_id,
                    seller_id=so.seller_id,
                    status=so.status,
                    subtotal=so.subtotal,
                    created_at=created_at,
                    items=items
                )
            )
        return output

    async def update_seller_order_status(
        self, seller_id: uuid.UUID, seller_order_id: uuid.UUID, new_status: str
    ) -> SellerOrderRead:
        stmt = (
            select(SellerOrder)
            .options(
                selectinload(SellerOrder.items),
                selectinload(SellerOrder.order)
            )
            .where(
                SellerOrder.id == seller_order_id,
                SellerOrder.seller_id == seller_id
            )
        )
        result = await self.session.execute(stmt)
        so = result.scalar_one_or_none()
        if not so:
            return None

        so.status = new_status
        await self.session.commit()
        await self.session.refresh(so)

        items = [
            SellerOrderItemRead(
                id=item.id,
                variant_id=item.variant_id,
                snapshot_name=item.snapshot_name,
                snapshot_price=item.snapshot_price,
                quantity=item.quantity
            )
            for item in so.items
        ]
        created_at = so.order.created_at if so.order else None
        return SellerOrderRead(
            id=so.id,
            order_id=so.order_id,
            seller_id=so.seller_id,
            status=so.status,
            subtotal=so.subtotal,
            created_at=created_at,
            items=items
        )

    async def get_seller_products(self, seller_id: uuid.UUID) -> List[SellerProductRead]:
        # Fetch seller offers join variant and product
        stmt = (
            select(
                Product.id.label("product_id"),
                Product.name.label("product_name"),
                Product.category_id,
                Product.brand_id,
                ProductVariant.id.label("variant_id"),
                ProductVariant.sku,
                ProductVariant.name.label("variant_name"),
                SellerOffer.price,
                SellerOffer.is_active,
                func.coalesce(Inventory.on_hand, 0).label("on_hand"),
                func.coalesce(Inventory.reserved, 0).label("reserved"),
                Warehouse.id.label("warehouse_id"),
                Warehouse.name.label("warehouse_name")
            )
            .select_from(SellerOffer)
            .join(ProductVariant, SellerOffer.variant_id == ProductVariant.id)
            .join(Product, ProductVariant.product_id == Product.id)
            .outerjoin(
                Inventory,
                and_(
                    Inventory.variant_id == ProductVariant.id,
                    Inventory.seller_id == seller_id
                )
            )
            .outerjoin(Warehouse, Inventory.warehouse_id == Warehouse.id)
            .where(SellerOffer.seller_id == seller_id)
        )
        result = await self.session.execute(stmt)
        rows = result.all()

        products = []
        for r in rows:
            on_hand = r.on_hand or 0
            reserved = r.reserved or 0
            available = max(0, on_hand - reserved)
            products.append(
                SellerProductRead(
                    product_id=r.product_id,
                    product_name=r.product_name,
                    category_id=r.category_id,
                    brand_id=r.brand_id,
                    variant_id=r.variant_id,
                    sku=r.sku,
                    variant_name=r.variant_name,
                    price=r.price,
                    is_active=r.is_active,
                    on_hand=on_hand,
                    reserved=reserved,
                    available=available,
                    warehouse_id=r.warehouse_id,
                    warehouse_name=r.warehouse_name
                )
            )
        return products

    async def create_seller_product(
        self, seller_id: uuid.UUID, data: SellerProductCreate
    ) -> SellerProductRead:
        # Create product
        product = Product(
            name=data.name,
            description=data.description,
            category_id=data.category_id,
            brand_id=data.brand_id,
            attributes=data.attributes or {},
            is_active=True
        )
        self.session.add(product)
        await self.session.flush()

        # Create variant
        variant = ProductVariant(
            product_id=product.id,
            sku=data.sku,
            name=data.variant_name,
            attributes=data.attributes or {}
        )
        self.session.add(variant)
        await self.session.flush()

        # Create offer
        offer = SellerOffer(
            seller_id=seller_id,
            variant_id=variant.id,
            price=data.price,
            is_active=True
        )
        self.session.add(offer)
        await self.session.flush()

        # Warehouse & Inventory
        warehouse_id = data.warehouse_id
        warehouse_name = None
        if not warehouse_id:
            # Find or create a default warehouse for this seller
            wh_stmt = select(Warehouse).where(Warehouse.seller_id == seller_id)
            wh_res = await self.session.execute(wh_stmt)
            default_wh = wh_res.scalars().first()
            if not default_wh:
                default_wh = Warehouse(seller_id=seller_id, name="Main Warehouse")
                self.session.add(default_wh)
                await self.session.flush()
            warehouse_id = default_wh.id
            warehouse_name = default_wh.name
        else:
            wh = await self.session.get(Warehouse, warehouse_id)
            if wh:
                warehouse_name = wh.name

        initial_stock = data.initial_stock or 0
        inv = Inventory(
            variant_id=variant.id,
            warehouse_id=warehouse_id,
            seller_id=seller_id,
            on_hand=initial_stock,
            reserved=0
        )
        self.session.add(inv)
        await self.session.flush()

        if initial_stock > 0:
            movement = InventoryMovement(
                inventory_id=inv.id,
                quantity_change=initial_stock,
                reason="INITIAL_STOCK"
            )
            self.session.add(movement)

        await self.session.commit()

        # Generate dummy embedding so product is searchable via pgvector
        search_service = SearchService(self.session)
        await search_service.generate_dummy_embedding_for_product(product.id)

        return SellerProductRead(
            product_id=product.id,
            product_name=product.name,
            category_id=product.category_id,
            brand_id=product.brand_id,
            variant_id=variant.id,
            sku=variant.sku,
            variant_name=variant.name,
            price=offer.price,
            is_active=offer.is_active,
            on_hand=initial_stock,
            reserved=0,
            available=initial_stock,
            warehouse_id=warehouse_id,
            warehouse_name=warehouse_name
        )

    async def get_seller_warehouses(self, seller_id: uuid.UUID) -> List[SellerWarehouseRead]:
        stmt = select(Warehouse).where(Warehouse.seller_id == seller_id)
        result = await self.session.execute(stmt)
        warehouses = result.scalars().all()
        return [SellerWarehouseRead.model_validate(w) for w in warehouses]

    async def create_seller_warehouse(self, seller_id: uuid.UUID, name: str) -> SellerWarehouseRead:
        wh = Warehouse(seller_id=seller_id, name=name)
        self.session.add(wh)
        await self.session.commit()
        await self.session.refresh(wh)
        return SellerWarehouseRead.model_validate(wh)
