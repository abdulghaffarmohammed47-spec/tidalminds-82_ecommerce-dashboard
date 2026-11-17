"""Ensure every active demo variant has a real seller offer and inventory."""

import asyncio

from sqlalchemy import select

from app.db.postgres import async_session_maker
from app.models.postgres.catalog import ProductVariant, Seller, SellerOffer
from app.models.postgres.commerce import Coupon
from app.models.postgres.inventory import Inventory, Warehouse


async def ensure_marketplace_data() -> None:
    async with async_session_maker() as session:
        welcome_coupon = (await session.execute(select(Coupon).where(Coupon.code == "WELCOME10"))).scalar_one_or_none()
        if welcome_coupon is None:
            session.add(Coupon(
                code="WELCOME10",
                usage_limit=1000,
                per_user_limit=1,
                discount_type="PERCENTAGE",
                discount_value=10,
                min_order_amount=10000,
                max_discount_amount=50000,
            ))

        variants = list(
            (
                await session.execute(
                    select(ProductVariant).join(ProductVariant.product).where(ProductVariant.product.has(is_active=True))
                )
            ).scalars().all()
        )
        sellers = list((await session.execute(select(Seller).where(Seller.is_active.is_(True)).order_by(Seller.id))).scalars().all())
        if not sellers:
            raise RuntimeError("At least one active seller is required before seeding offers")

        warehouses: dict[str, Warehouse] = {}
        for seller in sellers:
            warehouse = (
                await session.execute(
                    select(Warehouse).where(Warehouse.seller_id == seller.id).order_by(Warehouse.id).limit(1)
                )
            ).scalar_one_or_none()
            if warehouse is None:
                warehouse = Warehouse(seller_id=seller.id, name=f"{seller.company_name} Demo Warehouse")
                session.add(warehouse)
                await session.flush()
            warehouses[str(seller.id)] = warehouse

        created_offers = 0
        created_inventory = 0
        for index, variant in enumerate(variants):
            offer = (
                await session.execute(
                    select(SellerOffer)
                    .where(SellerOffer.variant_id == variant.id, SellerOffer.is_active.is_(True))
                    .limit(1)
                )
            ).scalar_one_or_none()
            if offer is None:
                seller = sellers[index % len(sellers)]
                offer = SellerOffer(
                    seller_id=seller.id,
                    variant_id=variant.id,
                    price=250000 + (index % 24) * 1750,
                    is_active=True,
                )
                session.add(offer)
                await session.flush()
                created_offers += 1
            else:
                seller = next(seller for seller in sellers if seller.id == offer.seller_id)

            inventory = (
                await session.execute(
                    select(Inventory)
                    .where(
                        Inventory.variant_id == variant.id,
                        Inventory.seller_id == seller.id,
                        Inventory.warehouse_id == warehouses[str(seller.id)].id,
                    )
                    .limit(1)
                )
            ).scalar_one_or_none()
            if inventory is None:
                session.add(
                    Inventory(
                        variant_id=variant.id,
                        warehouse_id=warehouses[str(seller.id)].id,
                        seller_id=seller.id,
                        on_hand=25 + (index % 75),
                        reserved=0,
                    )
                )
                created_inventory += 1

        await session.commit()
        print(f"Created {created_offers} seller offers and {created_inventory} inventory records.")


if __name__ == "__main__":
    asyncio.run(ensure_marketplace_data())
