import pytest
import uuid
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.postgres.catalog import Seller, SellerOffer
from app.models.postgres.inventory import Warehouse, Inventory

PASSWORD = "TestPassword123!"

async def create_user_and_login(async_client: AsyncClient, prefix: str) -> dict:
    uid = str(uuid.uuid4())
    email = f"{prefix}_{uid}@stress.com"
    reg_res = await async_client.post("/api/auth/register", json={
        "email": email,
        "password": PASSWORD,
        "full_name": f"Stress {prefix}"
    })
    assert reg_res.status_code == 200, reg_res.text
    login_res = await async_client.post("/api/auth/login", data={
        "username": email,
        "password": PASSWORD
    })
    token = login_res.json()["access_token"]
    return {"id": reg_res.json()["id"], "token": token, "headers": {"Authorization": f"Bearer {token}"}}

@pytest.mark.asyncio
async def test_high_volume_concurrency_flash_sale(async_client: AsyncClient, db_session: AsyncSession):
    """
    TC-32 / TC-33 Concurrency Stress Test:
    10 simultaneous buyers race to buy an item with ONLY 2 units available in stock.
    Guarantees:
      - Exactly 2 checkouts succeed (200 OK)
      - Exactly 8 checkouts receive 400 Insufficient Stock
      - Zero overselling, zero negative stock
    """
    # 1. Setup seller, warehouse, product, and inventory with stock=2
    seller_data = await create_user_and_login(async_client, "seller")
    seller = Seller(user_id=seller_data["id"], company_name=f"FlashSale Ltd {uuid.uuid4()}")
    db_session.add(seller)
    await db_session.commit()

    uid = str(uuid.uuid4())[:8]
    cat_res = await async_client.post("/api/categories/", json={"name": f"Cat {uid}", "slug": f"cat-{uid}", "description": ""})
    cat_id = cat_res.json()["id"]

    brand_res = await async_client.post("/api/products/brands", json={"name": f"Brand {uid}", "slug": f"brand-{uid}", "description": ""})
    brand_id = brand_res.json()["id"]

    prod_res = await async_client.post("/api/products/", json={
        "name": f"Flash Item {uid}",
        "description": "High demand item with only 2 units",
        "category_id": cat_id,
        "brand_id": brand_id,
        "variants": [{"name": f"Variant {uid}", "sku": f"FLASH-{uid}"}]
    })
    product = prod_res.json()
    prod_id = product["id"]
    variant_id = product["variants"][0]["id"]
    sku = product["variants"][0]["sku"]

    # Create warehouse & set stock to exactly 2
    wh = Warehouse(seller_id=seller.id, name=f"WH-{uid}")
    db_session.add(wh)
    await db_session.flush()

    inv = Inventory(
        variant_id=variant_id,
        warehouse_id=wh.id,
        seller_id=seller.id,
        on_hand=2,
        reserved=0
    )
    db_session.add(inv)

    offer = SellerOffer(
        seller_id=seller.id,
        variant_id=variant_id,
        price=199900,
        is_active=True
    )
    db_session.add(offer)
    await db_session.commit()

    # 2. Register 10 concurrent buyers
    buyers = await asyncio.gather(*[
        create_user_and_login(async_client, f"buyer_{i}") for i in range(10)
    ])

    # 3. All 10 buyers add 1 unit to cart
    async def add_to_cart(b):
        return await async_client.post("/api/cart/items", json={
            "product_id": prod_id,
            "variant_id": variant_id,
            "sku": sku,
            "quantity": 1
        }, headers=b["headers"])

    await asyncio.gather(*[add_to_cart(b) for b in buyers])

    # 4. Fire 10 simultaneous checkout requests using asyncio.gather
    async def run_checkout(b):
        return await async_client.post("/api/orders/checkout", json={}, headers=b["headers"])

    responses = await asyncio.gather(*[run_checkout(b) for b in buyers])

    statuses = [r.status_code for r in responses]
    success_count = statuses.count(200)
    failed_count = statuses.count(400)

    # 5. STRICT VERIFICATION
    assert success_count == 2, f"Expected exactly 2 successes, got {success_count}. Statuses: {statuses}"
    assert failed_count == 8, f"Expected exactly 8 rejections, got {failed_count}. Statuses: {statuses}"

    # Verify inventory in database: reserved must equal exactly 2, on_hand must still be 2
    await db_session.refresh(inv)
    assert inv.reserved == 2, f"Reserved stock must be 2, got {inv.reserved}"
    assert inv.on_hand == 2, f"On-hand stock must be 2, got {inv.on_hand}"

@pytest.mark.asyncio
async def test_deadlock_prevention_cross_item_orders(async_client: AsyncClient, db_session: AsyncSession):
    """
    TC-35 Deadlock Resistance Test:
    Buyer 1 adds [Item A, Item B] to cart.
    Buyer 2 adds [Item B, Item A] to cart.
    Both checkout simultaneously.
    Because OrderRepository enforces deterministic sort by variant_id,
    locks are acquired in the same global sequence, preventing cyclic deadlocks.
    """
    seller_data = await create_user_and_login(async_client, "seller_dl")
    seller = Seller(user_id=seller_data["id"], company_name=f"Deadlock Proof Ltd {uuid.uuid4()}")
    db_session.add(seller)
    await db_session.commit()

    uid = str(uuid.uuid4())[:8]
    cat_res = await async_client.post("/api/categories/", json={"name": f"Cat DL {uid}", "slug": f"cat-dl-{uid}", "description": ""})
    cat_id = cat_res.json()["id"]

    brand_res = await async_client.post("/api/products/brands", json={"name": f"Brand DL {uid}", "slug": f"brand-dl-{uid}", "description": ""})
    brand_id = brand_res.json()["id"]

    # Product A
    pA = (await async_client.post("/api/products/", json={
        "name": f"Product A {uid}",
        "description": "Item A",
        "category_id": cat_id,
        "brand_id": brand_id,
        "variants": [{"name": f"Var A {uid}", "sku": f"SKU-A-{uid}"}]
    })).json()
    var_a_id = pA["variants"][0]["id"]
    sku_a = pA["variants"][0]["sku"]

    # Product B
    pB = (await async_client.post("/api/products/", json={
        "name": f"Product B {uid}",
        "description": "Item B",
        "category_id": cat_id,
        "brand_id": brand_id,
        "variants": [{"name": f"Var B {uid}", "sku": f"SKU-B-{uid}"}]
    })).json()
    var_b_id = pB["variants"][0]["id"]
    sku_b = pB["variants"][0]["sku"]

    wh = Warehouse(seller_id=seller.id, name=f"WH-DL-{uid}")
    db_session.add(wh)
    await db_session.flush()

    inv_a = Inventory(variant_id=var_a_id, warehouse_id=wh.id, seller_id=seller.id, on_hand=10, reserved=0)
    inv_b = Inventory(variant_id=var_b_id, warehouse_id=wh.id, seller_id=seller.id, on_hand=10, reserved=0)
    db_session.add_all([inv_a, inv_b])

    offer_a = SellerOffer(seller_id=seller.id, variant_id=var_a_id, price=5000, is_active=True)
    offer_b = SellerOffer(seller_id=seller.id, variant_id=var_b_id, price=7500, is_active=True)
    db_session.add_all([offer_a, offer_b])
    await db_session.commit()

    buyer1 = await create_user_and_login(async_client, "dl_b1")
    buyer2 = await create_user_and_login(async_client, "dl_b2")

    # Buyer 1 adds A then B
    await async_client.post("/api/cart/items", json={"product_id": pA["id"], "variant_id": var_a_id, "sku": sku_a, "quantity": 1}, headers=buyer1["headers"])
    await async_client.post("/api/cart/items", json={"product_id": pB["id"], "variant_id": var_b_id, "sku": sku_b, "quantity": 1}, headers=buyer1["headers"])

    # Buyer 2 adds B then A (inverted sequence)
    await async_client.post("/api/cart/items", json={"product_id": pB["id"], "variant_id": var_b_id, "sku": sku_b, "quantity": 1}, headers=buyer2["headers"])
    await async_client.post("/api/cart/items", json={"product_id": pA["id"], "variant_id": var_a_id, "sku": sku_a, "quantity": 1}, headers=buyer2["headers"])

    # Concurrently checkout
    res1, res2 = await asyncio.gather(
        async_client.post("/api/orders/checkout", json={}, headers=buyer1["headers"]),
        async_client.post("/api/orders/checkout", json={}, headers=buyer2["headers"])
    )

    # Both must succeed cleanly without deadlocks
    assert res1.status_code == 200, f"Buyer 1 failed: {res1.text}"
    assert res2.status_code == 200, f"Buyer 2 failed: {res2.text}"

    await db_session.refresh(inv_a)
    await db_session.refresh(inv_b)
    assert inv_a.reserved == 2
    assert inv_b.reserved == 2
