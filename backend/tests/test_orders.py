import pytest
import pytest_asyncio
from httpx import AsyncClient
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.postgres.catalog import Seller, SellerOffer
from app.models.postgres.inventory import Warehouse, Inventory
from app.models.postgres.auth import User
from app.models.postgres.system import OutboxEvent
from app.models.postgres.commerce import Coupon, CouponRedemption, SellerOrder
from app.models.postgres.shipping import Shipment, Return
from sqlalchemy import select, func

@pytest_asyncio.fixture
async def registered_user(async_client: AsyncClient):
    email = f"user_{uuid.uuid4()}@orders.com"
    res = await async_client.post("/api/auth/register", json={
        "email": email,
        "password": "password123",
        "full_name": "Order User"
    })
    assert res.status_code == 200
    
    login_res = await async_client.post("/api/auth/login", data={
        "username": email,
        "password": "password123"
    })
    return {"user": res.json(), "token": login_res.json()["access_token"]}

@pytest_asyncio.fixture
async def sample_seller_offer(async_client: AsyncClient, db_session: AsyncSession):
    # Register user to be seller
    uid = str(uuid.uuid4())
    email = f"seller_{uid}@orders.com"
    res = await async_client.post("/api/auth/register", json={
        "email": email,
        "password": "password123",
        "full_name": "Seller User"
    })
    seller_user_id = res.json()["id"]

    # Create seller
    seller = Seller(user_id=seller_user_id, company_name="Order Seller Ltd")
    db_session.add(seller)
    await db_session.flush()

    # Create category, brand, product, variant via API
    cat_res = await async_client.post("/api/categories/", json={"name": f"Cat {uid}", "slug": f"cat-{uid}", "description": ""})
    cat_id = cat_res.json()["id"]

    brand_res = await async_client.post("/api/products/brands", json={"name": f"Brand {uid}", "slug": f"brand-{uid}", "description": ""})
    brand_id = brand_res.json()["id"]

    prod_res = await async_client.post("/api/products/", json={
        "name": f"Product {uid}",
        "description": "Test product for orders",
        "category_id": cat_id,
        "brand_id": brand_id,
        "variants": [{"name": f"Variant {uid}", "sku": f"SKU-{uid}"}]
    })
    product = prod_res.json()
    variant_id = product["variants"][0]["id"]
    sku = product["variants"][0]["sku"]

    # Create SellerOffer
    offer = SellerOffer(
        seller_id=seller.id,
        variant_id=variant_id,
        price=5000, # 50.00 INR
        is_active=True
    )
    db_session.add(offer)
    await db_session.flush()

    # Create a Warehouse + Inventory so stock reservation succeeds during checkout
    warehouse = Warehouse(seller_id=seller.id, name="Test Warehouse")
    db_session.add(warehouse)
    await db_session.flush()

    inventory = Inventory(
        variant_id=variant_id,
        warehouse_id=warehouse.id,
        seller_id=seller.id,
        on_hand=100,
        reserved=0
    )
    db_session.add(inventory)
    await db_session.commit()

    return {
        "product_id": product["id"],
        "variant_id": variant_id,
        "sku": sku,
        "price": 5000,
        "seller_id": seller.id
    }

@pytest.mark.asyncio
async def test_checkout_and_payment_flow(async_client: AsyncClient, registered_user, sample_seller_offer):
    headers = {"Authorization": f"Bearer {registered_user['token']}"}

    # 1. Add item to cart
    add_res = await async_client.post(
        "/api/cart/items", 
        json={
            "product_id": sample_seller_offer["product_id"],
            "variant_id": sample_seller_offer["variant_id"],
            "sku": sample_seller_offer["sku"],
            "quantity": 2
        },
        headers=headers
    )
    assert add_res.status_code == 200

    # 2. Checkout
    checkout_res = await async_client.post("/api/orders/checkout", json={}, headers=headers)
    assert checkout_res.status_code == 200
    order = checkout_res.json()
    assert order["status"] == "PENDING_PAYMENT"
    assert order["total_amount"] == 5000 * 2
    assert len(order["seller_orders"]) == 1
    assert len(order["seller_orders"][0]["items"]) == 1
    order_id = order["id"]

    # 3. Verify cart is cleared
    cart_res = await async_client.get("/api/cart", headers=headers)
    assert len(cart_res.json()["items"]) == 0

    # 4. Simulate Payment Success
    pay_res = await async_client.post(f"/api/payments/{order_id}/simulate", json={"status": "SUCCESS"}, headers=headers)
    assert pay_res.status_code == 200
    assert pay_res.json()["status"] == "SUCCESS"

    # 5. Verify Order Status updated
    orders_res = await async_client.get("/api/orders", headers=headers)
    assert orders_res.status_code == 200
    orders = orders_res.json()
    assert len(orders) > 0
    assert orders[0]["id"] == order_id
    assert orders[0]["status"] == "PAID"
    assert orders[0]["seller_orders"][0]["status"] == "PROCESSING"


@pytest.mark.asyncio
async def test_coupon_is_validated_and_redeemed_once(async_client, db_session, registered_user, sample_seller_offer):
    coupon_code = f"SAVE{uuid.uuid4().hex[:8].upper()}"
    db_session.add(Coupon(
        code=coupon_code,
        usage_limit=10,
        per_user_limit=1,
        discount_type="PERCENTAGE",
        discount_value=10,
        min_order_amount=10000,
        max_discount_amount=2000,
    ))
    await db_session.commit()
    headers = {"Authorization": f"Bearer {registered_user['token']}"}

    validation = await async_client.post("/api/v1/coupons/validate", json={"code": coupon_code.lower()}, headers=headers)
    assert validation.status_code == 200
    assert validation.json()["discount_value"] == 10

    await async_client.post("/api/cart/items", json={
        "product_id": sample_seller_offer["product_id"],
        "variant_id": sample_seller_offer["variant_id"],
        "sku": sample_seller_offer["sku"],
        "quantity": 2,
    }, headers=headers)
    checkout = await async_client.post(
        "/api/orders/checkout",
        json={"coupon_code": coupon_code},
        headers=headers,
    )
    assert checkout.status_code == 200
    assert checkout.json()["total_amount"] == 9000

    redemption_count = await db_session.scalar(
        select(func.count(CouponRedemption.id)).where(CouponRedemption.user_id == registered_user["user"]["id"])
    )
    assert redemption_count == 1


@pytest.mark.asyncio
async def test_customer_can_read_tracking_only_for_owned_order(async_client, db_session, registered_user, sample_seller_offer):
    headers = {"Authorization": f"Bearer {registered_user['token']}"}
    await async_client.post("/api/cart/items", json={
        "product_id": sample_seller_offer["product_id"],
        "variant_id": sample_seller_offer["variant_id"],
        "sku": sample_seller_offer["sku"],
        "quantity": 1,
    }, headers=headers)
    checkout = await async_client.post("/api/orders/checkout", json={}, headers=headers)
    assert checkout.status_code == 200
    order = checkout.json()
    seller_order_id = order["seller_orders"][0]["id"]
    db_session.add(Shipment(
        seller_order_id=seller_order_id,
        provider="MOCK",
        tracking_number=f"MOCK-TEST-{uuid.uuid4().hex[:10].upper()}",
        status="IN_TRANSIT",
    ))
    await db_session.commit()

    tracking = await async_client.get(f"/api/v1/shipping/orders/{order['id']}", headers=headers)
    assert tracking.status_code == 200
    assert tracking.json()[0]["provider"] == "MOCK"


@pytest.mark.asyncio
async def test_customer_can_request_return_for_owned_shipped_order(async_client, db_session, registered_user, sample_seller_offer):
    headers = {"Authorization": f"Bearer {registered_user['token']}"}
    await async_client.post("/api/cart/items", json={
        "product_id": sample_seller_offer["product_id"],
        "variant_id": sample_seller_offer["variant_id"],
        "sku": sample_seller_offer["sku"],
        "quantity": 1,
    }, headers=headers)
    checkout = await async_client.post("/api/orders/checkout", json={}, headers=headers)
    order = checkout.json()
    seller_order_id = order["seller_orders"][0]["id"]
    seller_order = (await db_session.execute(select(SellerOrder).where(SellerOrder.id == seller_order_id))).scalar_one()
    seller_order.status = "SHIPPED"
    await db_session.commit()

    requested = await async_client.post(
        f"/api/v1/returns/seller-orders/{seller_order_id}",
        json={"reason": "Item arrived damaged"},
        headers=headers,
    )
    assert requested.status_code == 200
    assert requested.json()["status"] == "REQUESTED"

    duplicate = await async_client.post(
        f"/api/v1/returns/seller-orders/{seller_order_id}",
        json={"reason": "Duplicate request"},
        headers=headers,
    )
    assert duplicate.status_code == 200
    assert duplicate.json()["id"] == requested.json()["id"]

@pytest.mark.asyncio
async def test_payment_failure_flow(async_client: AsyncClient, registered_user, sample_seller_offer):
    headers = {"Authorization": f"Bearer {registered_user['token']}"}

    # Add to cart and checkout
    await async_client.post("/api/cart/items", json={
        "product_id": sample_seller_offer["product_id"],
        "variant_id": sample_seller_offer["variant_id"],
        "sku": sample_seller_offer["sku"],
        "quantity": 1
    }, headers=headers)
    
    checkout_res = await async_client.post("/api/orders/checkout", json={}, headers=headers)
    order_id = checkout_res.json()["id"]

    # Simulate Payment Failure
    pay_res = await async_client.post(f"/api/payments/{order_id}/simulate", json={"status": "FAILED"}, headers=headers)
    assert pay_res.status_code == 200

    # Verify Order Status
    orders_res = await async_client.get("/api/orders", headers=headers)
    assert orders_res.json()[0]["status"] == "PAYMENT_FAILED"

@pytest.mark.asyncio
async def test_customer_cannot_simulate_payment_for_another_customer_order(
    async_client, registered_user, sample_seller_offer
):
    owner_headers = {"Authorization": f"Bearer {registered_user['token']}"}
    await async_client.post("/api/cart/items", json={
        "product_id": sample_seller_offer["product_id"],
        "variant_id": sample_seller_offer["variant_id"],
        "sku": sample_seller_offer["sku"],
        "quantity": 1,
    }, headers=owner_headers)
    checkout = await async_client.post("/api/orders/checkout", json={}, headers=owner_headers)
    assert checkout.status_code == 200

    other_email = f"other_{uuid.uuid4()}@orders.com"
    await async_client.post("/api/auth/register", json={
        "email": other_email,
        "password": "password123",
        "full_name": "Other User",
    })
    login = await async_client.post("/api/auth/login", data={
        "username": other_email,
        "password": "password123",
    })
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    payment = await async_client.post(
        f"/api/payments/{checkout.json()['id']}/simulate",
        json={"status": "SUCCESS"},
        headers=other_headers,
    )
    assert payment.status_code == 404

@pytest.mark.asyncio
async def test_checkout_idempotency_and_outbox(async_client, db_session, registered_user, sample_seller_offer):
    headers = {
        "Authorization": f"Bearer {registered_user['token']}",
        "Idempotency-Key": f"checkout-{uuid.uuid4()}",
    }
    await async_client.post("/api/cart/items", json={
        "product_id": sample_seller_offer["product_id"],
        "variant_id": sample_seller_offer["variant_id"],
        "sku": sample_seller_offer["sku"],
        "quantity": 1,
    }, headers=headers)

    first = await async_client.post("/api/orders/checkout", json={}, headers=headers)
    second = await async_client.post("/api/orders/checkout", json={}, headers=headers)

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["id"] == first.json()["id"]

    result = await db_session.execute(
        select(OutboxEvent).where(OutboxEvent.topic == "OrderCreated")
    )
    matching_events = [
        event for event in result.scalars().all()
        if event.payload.get("order_id") == first.json()["id"]
    ]
    assert len(matching_events) == 1
