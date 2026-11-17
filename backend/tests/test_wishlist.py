import uuid

import pytest
import pytest_asyncio
from app.models.postgres.catalog import Seller, SellerOffer
from app.models.postgres.inventory import Warehouse, Inventory


@pytest_asyncio.fixture
async def wishlist_user(async_client):
    email = f"wishlist_{uuid.uuid4()}@test.com"
    response = await async_client.post("/api/auth/register", json={
        "email": email,
        "password": "password123",
        "full_name": "Wishlist User",
    })
    login = await async_client.post("/api/auth/login", data={
        "username": email,
        "password": "password123",
    })
    return {"token": login.json()["access_token"]}


@pytest_asyncio.fixture
async def wishlist_product(async_client, db_session):
    uid = str(uuid.uuid4())
    seller_user = await async_client.post("/api/auth/register", json={
        "email": f"seller_{uid}@test.com",
        "password": "password123",
    })
    seller = Seller(user_id=seller_user.json()["id"], company_name=f"Wishlist Seller {uid}")
    db_session.add(seller)
    await db_session.flush()
    category = (await async_client.post("/api/categories/", json={"name": f"Wishlist Cat {uid}", "slug": f"wishlist-{uid}", "description": ""})).json()
    brand = (await async_client.post("/api/products/brands", json={"name": f"Wishlist Brand {uid}", "slug": f"wishlist-brand-{uid}", "description": ""})).json()
    product = (await async_client.post("/api/products/", json={
        "name": f"Wishlist Product {uid}",
        "category_id": category["id"],
        "brand_id": brand["id"],
        "variants": [{"name": "Default", "sku": f"WISH-{uid}"}],
    })).json()
    return product["id"]


@pytest.mark.asyncio
async def test_wishlist_is_user_scoped_and_duplicate_safe(async_client, wishlist_user, wishlist_product):
    headers = {"Authorization": f"Bearer {wishlist_user['token']}"}
    product_id = wishlist_product

    added = await async_client.post(
        "/api/v1/wishlist",
        json={"product_id": product_id},
        headers=headers,
    )
    assert added.status_code == 201
    assert added.json()["product_id"] == product_id

    duplicate = await async_client.post(
        "/api/v1/wishlist",
        json={"product_id": product_id},
        headers=headers,
    )
    assert duplicate.status_code == 409

    listed = await async_client.get("/api/v1/wishlist", headers=headers)
    assert listed.status_code == 200
    assert [item["product_id"] for item in listed.json()] == [product_id]

    removed = await async_client.delete(f"/api/v1/wishlist/{product_id}", headers=headers)
    assert removed.status_code == 204

    empty = await async_client.get("/api/v1/wishlist", headers=headers)
    assert empty.json() == []


@pytest.mark.asyncio
async def test_wishlist_rejects_unauthenticated_access(async_client, wishlist_product):
    response = await async_client.get("/api/v1/wishlist")
    assert response.status_code == 401
