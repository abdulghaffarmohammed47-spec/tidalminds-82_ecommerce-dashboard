import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_seller_portal_full_flow(async_client: AsyncClient):
    uid = uuid.uuid4().hex[:6]
    seller_email = f"seller_portal_{uid}@example.com"
    buyer_email = f"buyer_portal_{uid}@example.com"
    password = "password123"

    # 1. Register and Login Seller
    await async_client.post("/api/auth/register", json={"email": seller_email, "password": password, "full_name": "Portal Seller"})
    seller_login = await async_client.post("/api/auth/login", data={"username": seller_email, "password": password})
    seller_token = seller_login.json()["access_token"]
    seller_headers = {"Authorization": f"Bearer {seller_token}"}

    # 2. Register and Login Buyer
    await async_client.post("/api/auth/register", json={"email": buyer_email, "password": password, "full_name": "Portal Buyer"})
    buyer_login = await async_client.post("/api/auth/login", data={"username": buyer_email, "password": password})
    buyer_token = buyer_login.json()["access_token"]
    buyer_headers = {"Authorization": f"Bearer {buyer_token}"}

    # 3. Apply to be seller
    apply_res = await async_client.post("/api/sellers/apply", json={"company_name": f"Nexus Tech {uid}"}, headers=seller_headers)
    assert apply_res.status_code == 200
    seller_id = apply_res.json()["id"]

    # 4. Check initial metrics
    metrics_res = await async_client.get("/api/sellers/me/metrics", headers=seller_headers)
    assert metrics_res.status_code == 200
    metrics = metrics_res.json()
    assert metrics["active_listings"] == 0
    assert metrics["total_orders"] == 0
    assert metrics["total_sales"] == 0

    # 5. List and create warehouses
    wh_list_res = await async_client.get("/api/sellers/me/warehouses", headers=seller_headers)
    assert wh_list_res.status_code == 200
    warehouses = wh_list_res.json()
    assert len(warehouses) >= 1
    default_wh_id = warehouses[0]["id"]

    create_wh_res = await async_client.post(
        "/api/sellers/me/warehouses",
        json={"name": f"East Hub {uid}"},
        headers=seller_headers
    )
    assert create_wh_res.status_code == 200
    new_wh_id = create_wh_res.json()["id"]

    # 6. Create category & brand
    cat_res = await async_client.post("/api/categories/", json={"name": f"Electronics {uid}", "slug": f"elec-{uid}", "description": ""})
    assert cat_res.status_code == 200
    cat_id = cat_res.json()["id"]

    brand_res = await async_client.post("/api/products/brands", json={"name": f"Sony {uid}", "slug": f"sony-{uid}", "description": ""})
    assert brand_res.status_code == 200
    brand_id = brand_res.json()["id"]

    # 7. Create product via Seller Portal endpoint
    prod_payload = {
        "name": f"Wireless Headphones {uid}",
        "description": "Noise cancelling premium headphones",
        "category_id": cat_id,
        "brand_id": brand_id,
        "sku": f"WH-1000XM5-{uid}",
        "variant_name": "Silver Edition",
        "price": 29999, # 299.99
        "attributes": {"color": "Silver", "connectivity": "Bluetooth 5.2"},
        "warehouse_id": new_wh_id,
        "initial_stock": 50
    }
    prod_res = await async_client.post("/api/sellers/me/products", json=prod_payload, headers=seller_headers)
    assert prod_res.status_code == 200
    prod_data = prod_res.json()
    assert prod_data["sku"] == f"WH-1000XM5-{uid}"
    assert prod_data["on_hand"] == 50
    assert prod_data["available"] == 50
    variant_id = prod_data["variant_id"]

    # 8. List seller products
    prods_list_res = await async_client.get("/api/sellers/me/products", headers=seller_headers)
    assert prods_list_res.status_code == 200
    my_products = prods_list_res.json()
    assert len(my_products) >= 1
    assert any(p["sku"] == f"WH-1000XM5-{uid}" for p in my_products)

    # 9. Adjust stock (relative delta +25 to existing 50)
    adjust_res = await async_client.post(
        "/api/sellers/me/inventory/adjust",
        json={
            "variant_id": variant_id,
            "warehouse_id": new_wh_id,
            "on_hand": 25
        },
        headers=seller_headers
    )
    assert adjust_res.status_code == 200
    assert adjust_res.json()["available"] == 75


    # 10. Buyer adds to cart and checks out
    add_cart_res = await async_client.post(
        "/api/cart/items",
        json={
            "product_id": prod_data["product_id"],
            "variant_id": variant_id,
            "sku": f"WH-1000XM5-{uid}",
            "quantity": 2
        },
        headers=buyer_headers
    )
    assert add_cart_res.status_code == 200

    checkout_res = await async_client.post("/api/orders/checkout", json={}, headers=buyer_headers)
    assert checkout_res.status_code == 200
    order_data = checkout_res.json()
    order_id = order_data["id"]

    # Simulate payment success
    await async_client.post(f"/api/payments/{order_id}/simulate", json={"status": "SUCCESS"}, headers=buyer_headers)

    # 11. Seller views orders
    seller_orders_res = await async_client.get("/api/sellers/me/orders", headers=seller_headers)
    assert seller_orders_res.status_code == 200
    seller_orders = seller_orders_res.json()
    assert len(seller_orders) >= 1
    target_seller_order = next((so for so in seller_orders if str(so["order_id"]) == str(order_id)), None)
    assert target_seller_order is not None
    assert target_seller_order["status"] == "PROCESSING"
    seller_order_id = target_seller_order["id"]

    # 12. Seller updates status to SHIPPED then DELIVERED
    update_res = await async_client.put(
        f"/api/sellers/me/orders/{seller_order_id}/status",
        json={"status": "SHIPPED"},
        headers=seller_headers
    )
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "SHIPPED"

    update_res2 = await async_client.put(
        f"/api/sellers/me/orders/{seller_order_id}/status",
        json={"status": "DELIVERED"},
        headers=seller_headers
    )
    assert update_res2.status_code == 200
    assert update_res2.json()["status"] == "DELIVERED"

    # 13. Verify metrics reflect the order
    updated_metrics_res = await async_client.get("/api/sellers/me/metrics", headers=seller_headers)
    assert updated_metrics_res.status_code == 200
    new_metrics = updated_metrics_res.json()
    assert new_metrics["total_orders"] >= 1
    assert new_metrics["total_sales"] >= 29999 * 2
    assert new_metrics["active_listings"] >= 1
