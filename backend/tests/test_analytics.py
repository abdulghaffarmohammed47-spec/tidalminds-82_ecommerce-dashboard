import pytest
# pyrefly: ignore [missing-import]
import pytest_asyncio
from httpx import AsyncClient
import uuid

@pytest_asyncio.fixture
async def registered_user(async_client: AsyncClient):
    email = f"user_{uuid.uuid4()}@analytics.com"
    res = await async_client.post("/api/auth/register", json={
        "email": email,
        "password": "password123",
        "full_name": "Analytics User"
    })
    assert res.status_code == 200
    
    login_res = await async_client.post("/api/auth/login", data={
        "username": email,
        "password": "password123"
    })
    return {"user": res.json(), "token": login_res.json()["access_token"]}

@pytest.mark.asyncio
async def test_analytics_log_event(async_client: AsyncClient, registered_user: dict):
    headers = {"Authorization": f"Bearer {registered_user['token']}"}
    
    res = await async_client.post(
        "/api/analytics/event",
        headers=headers,
        json={
            "event_type": "view_product",
            "product_id": str(uuid.uuid4()),
            "metadata": {"source": "homepage"}
        }
    )
    
    assert res.status_code == 200
    assert res.json() == {"success": True}

@pytest.mark.asyncio
async def test_analytics_trending(async_client: AsyncClient):
    res = await async_client.get("/api/analytics/trending")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

@pytest.mark.asyncio
async def test_analytics_recommendations(async_client: AsyncClient):
    product_id = str(uuid.uuid4())
    res = await async_client.get(f"/api/analytics/recommendations/{product_id}")
    assert res.status_code == 200
    assert isinstance(res.json(), list)
