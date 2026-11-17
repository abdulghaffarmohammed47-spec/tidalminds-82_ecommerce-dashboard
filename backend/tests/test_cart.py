import pytest
# pyrefly: ignore [missing-import]
import pytest_asyncio
from httpx import AsyncClient
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.postgres.catalog import Seller, SellerOffer

@pytest_asyncio.fixture
async def sample_product(async_client: AsyncClient, db_session: AsyncSession):
    uid = str(uuid.uuid4())
    # Create category
    cat_res = await async_client.post("/api/categories/", json={"name": f"Cat {uid}", "slug": f"cat-{uid}", "description": ""})
    assert cat_res.status_code == 200, cat_res.text
    cat_id = cat_res.json()["id"]

    # Create brand
    brand_res = await async_client.post("/api/products/brands", json={"name": f"Brand {uid}", "slug": f"brand-{uid}", "description": ""})
    assert brand_res.status_code == 200, brand_res.text
    brand_id = brand_res.json()["id"]

    # Create product
    prod_data = {
        "name": f"Product {uid}",
        "description": "Test product",
        "category_id": cat_id,
        "brand_id": brand_id,
        "variants": [
            {
                "name": f"Variant {uid}",
                "sku": f"SKU-{uid}",
                "attributes": {"color": "red"}
            }
        ]
    }
    prod_res = await async_client.post("/api/products/", json=prod_data)
    assert prod_res.status_code == 200, prod_res.text

    seller_email = f"seller_{uid}@cart.com"
    seller_res = await async_client.post("/api/auth/register", json={
        "email": seller_email,
        "password": "password123",
        "full_name": "Cart Seller",
    })
    assert seller_res.status_code == 200, seller_res.text
    seller = Seller(user_id=seller_res.json()["id"], company_name="Cart Seller")
    db_session.add(seller)
    await db_session.flush()
    db_session.add(SellerOffer(
        seller_id=seller.id,
        variant_id=prod_res.json()["variants"][0]["id"],
        price=2500,
        is_active=True,
    ))
    await db_session.commit()
    return prod_res.json()

@pytest_asyncio.fixture
async def registered_user(async_client: AsyncClient):
    email = f"user_{uuid.uuid4()}@cart.com"
    res = await async_client.post("/api/auth/register", json={
        "email": email,
        "password": "password123",
        "full_name": "Cart User"
    })
    assert res.status_code == 200
    
    login_res = await async_client.post("/api/auth/login", data={
        "username": email,
        "password": "password123"
    })
    assert login_res.status_code == 200
    return {"user": res.json(), "token": login_res.json()["access_token"]}

@pytest.mark.asyncio
async def test_guest_cart_flow(async_client: AsyncClient, sample_product):
    session_id = str(uuid.uuid4())
    headers = {"X-Session-ID": session_id}
    
    product_id = sample_product["id"]
    variant_id = sample_product["variants"][0]["id"]
    sku = sample_product["variants"][0]["sku"]

    # Add to cart
    add_res = await async_client.post(
        "/api/cart/items", 
        json={
            "product_id": product_id,
            "variant_id": variant_id,
            "sku": sku,
            "quantity": 2
        },
        headers=headers
    )
    assert add_res.status_code == 200
    cart = add_res.json()
    assert cart["id"] == session_id
    assert len(cart["items"]) == 1
    assert cart["items"][0]["quantity"] == 2
    # Cart stores the active seller offer price in minor currency units.
    assert cart["total_price"] == 2500 * 2

    # Get cart
    get_res = await async_client.get("/api/cart", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["total_price"] == 2500 * 2

    # Update item
    upd_res = await async_client.put(
        f"/api/cart/items/{sku}",
        json={"quantity": 3},
        headers=headers
    )
    assert upd_res.status_code == 200
    assert upd_res.json()["items"][0]["quantity"] == 3

    # Remove item
    del_res = await async_client.delete(f"/api/cart/items/{sku}", headers=headers)
    assert del_res.status_code == 200
    assert len(del_res.json()["items"]) == 0

@pytest.mark.asyncio
async def test_cart_merge(async_client: AsyncClient, sample_product, registered_user):
    session_id = str(uuid.uuid4())
    guest_headers = {"X-Session-ID": session_id}
    user_headers = {"Authorization": f"Bearer {registered_user['token']}"}
    
    product_id = sample_product["id"]
    variant_id = sample_product["variants"][0]["id"]
    sku = sample_product["variants"][0]["sku"]

    # Add item to guest cart
    await async_client.post(
        "/api/cart/items", 
        json={
            "product_id": product_id,
            "variant_id": variant_id,
            "sku": sku,
            "quantity": 2
        },
        headers=guest_headers
    )

    # Add same item to user cart
    await async_client.post(
        "/api/cart/items", 
        json={
            "product_id": product_id,
            "variant_id": variant_id,
            "sku": sku,
            "quantity": 1
        },
        headers=user_headers
    )

    # Merge guest cart into user cart
    merge_res = await async_client.post(f"/api/cart/merge?guest_session_id={session_id}", headers=user_headers)
    assert merge_res.status_code == 200
    merged_cart = merge_res.json()
    
    # Should have 3 quantity (2 from guest + 1 from user)
    assert len(merged_cart["items"]) == 1
    assert merged_cart["items"][0]["quantity"] == 3

    # Guest cart should be empty now
    guest_get_res = await async_client.get("/api/cart", headers=guest_headers)
    assert guest_get_res.status_code == 200
    assert len(guest_get_res.json()["items"]) == 0
