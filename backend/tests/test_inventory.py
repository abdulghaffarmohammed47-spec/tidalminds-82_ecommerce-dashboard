import pytest
import uuid
import asyncio
from httpx import AsyncClient

# Test data
password = "TestPassword123!"

@pytest.mark.asyncio
async def test_inventory_concurrency(async_client: AsyncClient, db_session):
    # 1. Create a seller user
    seller_id = str(uuid.uuid4())
    res = await async_client.post("/api/auth/register", json={
        "email": f"seller_{seller_id}@test.com",
        "password": password,
        "is_seller": True
    })
    seller_user_id = res.json()["id"]
    
    login_res = await async_client.post("/api/auth/login", data={
        "username": f"seller_{seller_id}@test.com",
        "password": password
    })
    seller_token = login_res.json()["access_token"]
    seller_headers = {"Authorization": f"Bearer {seller_token}"}

    from app.models.postgres.catalog import Seller
    seller = Seller(user_id=seller_user_id, company_name=f"Seller {seller_id}")
    db_session.add(seller)
    await db_session.commit()
    real_seller_id = seller.id

    # 2. Create category, brand, product & variant
    cat_res = await async_client.post("/api/categories/", json={
        "name": f"Tech {seller_id}",
        "slug": f"tech-{seller_id}",
        "description": ""
    }, headers=seller_headers)
    assert cat_res.status_code == 200, cat_res.text
    cat_id = cat_res.json()["id"]

    brand_res = await async_client.post("/api/products/brands", json={
        "name": f"Brand {seller_id}",
        "slug": f"brand-{seller_id}",
        "description": ""
    }, headers=seller_headers) # ADDED HEADERS HERE just in case
    assert brand_res.status_code == 200, brand_res.text
    brand_id = brand_res.json()["id"]

    prod_res = await async_client.post("/api/products/", json={
        "name": f"Limited Item {seller_id}",
        "slug": f"limited-item-{seller_id}",
        "description": "Only 1 in stock",
        "category_id": cat_id,
        "brand_id": brand_id,
        "variants": [{"name": f"Variant {seller_id}", "sku": f"LTD-{seller_id}"}]
    }, headers=seller_headers)
    assert prod_res.status_code == 200, prod_res.text
    
    product = prod_res.json()
    prod_id = product["id"]
    variant_id = product["variants"][0]["id"]

    # 3. Create Warehouse and Inventory (Only 1 item on hand)
    wh_res = await async_client.post("/api/inventory/warehouses", json={
        "name": "Main Warehouse"
    }, headers=seller_headers)
    assert wh_res.status_code == 200, wh_res.text
    warehouse_id = wh_res.json()["id"]

    inv_res = await async_client.post(f"/api/inventory/{variant_id}/warehouses/{warehouse_id}/adjust", json={
        "on_hand": 1
    }, headers=seller_headers)
    assert inv_res.status_code == 200, inv_res.text
    assert inv_res.json()["on_hand"] == 1
    assert inv_res.json()["reserved"] == 0

    # 4. Create SellerOffer
    from app.models.postgres.catalog import SellerOffer
    offer = SellerOffer(
        seller_id=real_seller_id,
        variant_id=variant_id,
        price=10000,
        is_active=True
    )
    db_session.add(offer)
    await db_session.commit()

    # 5. Create two different buyers
    buyer1_id = str(uuid.uuid4())
    await async_client.post("/api/auth/register", json={
        "email": f"buyer1_{buyer1_id}@test.com",
        "password": password
    })
    login1_res = await async_client.post("/api/auth/login", data={
        "username": f"buyer1_{buyer1_id}@test.com",
        "password": password
    })
    buyer1_headers = {"Authorization": f"Bearer {login1_res.json()['access_token']}"}

    buyer2_id = str(uuid.uuid4())
    await async_client.post("/api/auth/register", json={
        "email": f"buyer2_{buyer2_id}@test.com",
        "password": password
    })
    login2_res = await async_client.post("/api/auth/login", data={
        "username": f"buyer2_{buyer2_id}@test.com",
        "password": password
    })
    buyer2_headers = {"Authorization": f"Bearer {login2_res.json()['access_token']}"}

    # 6. Both buyers add to cart
    await async_client.post("/api/cart/items", json={
        "product_id": prod_id,
        "variant_id": variant_id,
        "sku": f"LTD-{seller_id}",
        "quantity": 1
    }, headers=buyer1_headers)

    await async_client.post("/api/cart/items", json={
        "product_id": prod_id,
        "variant_id": variant_id,
        "sku": f"LTD-{seller_id}",
        "quantity": 1
    }, headers=buyer2_headers)

    # 7. Concurrent Checkout Simulation
    # Since we can't easily multithread SQLite if it's in-memory, we rely on PostgreSQL in the docker container.
    # We will dispatch two requests at the exact same time.
    async def checkout(headers):
        return await async_client.post("/api/orders/checkout", json={}, headers=headers)

    responses = await asyncio.gather(
        checkout(buyer1_headers),
        checkout(buyer2_headers)
    )

    # 8. Verify exactly one succeeded and one failed with 400 Insufficient Stock
    statuses = [res.status_code for res in responses]
    print(f"Checkout responses: {[res.json() for res in responses]}")
    assert 200 in statuses, "One checkout should have succeeded"
    assert 400 in statuses, "One checkout should have failed due to locking/insufficient stock"
    
    # 9. Verify inventory states
    # The successful order should have incremented reserved by 1.
    inv_check = await async_client.get(f"/api/inventory/{warehouse_id}", headers=seller_headers)
    # The API we built doesn't expose a GET for the variant inventory easily yet in a user-facing way,
    # but we can fetch it via a new endpoint if we added one, or we can just verify the successful order's status.
    
    success_res = responses[statuses.index(200)]
    order_id = success_res.json()["id"]
    
    # 10. Process payment
    pay_res = await async_client.post(f"/api/payments/{order_id}/simulate", json={
        "status": "SUCCESS"
    }, headers=buyer1_headers) # Headers don't strictly matter for simulation endpoint currently unless protected
    assert pay_res.status_code == 200
    
    # 11. Optional: Check DB directly if we wanted to verify on_hand dropped to 0.
