import pytest
# pyrefly: ignore [missing-import]
import pytest_asyncio
from httpx import AsyncClient
import uuid

@pytest_asyncio.fixture
async def registered_user(async_client: AsyncClient):
    email = f"user_{uuid.uuid4()}@bot.com"
    res = await async_client.post("/api/auth/register", json={
        "email": email,
        "password": "password123",
        "full_name": "Bot User"
    })
    assert res.status_code == 200
    
    login_res = await async_client.post("/api/auth/login", data={
        "username": email,
        "password": "password123"
    })
    return {"user": res.json(), "token": login_res.json()["access_token"]}

@pytest.mark.asyncio
async def test_bot_order_intent(async_client: AsyncClient, registered_user: dict):
    headers = {"Authorization": f"Bearer {registered_user['token']}"}
    
    res = await async_client.post(
        "/api/bot/chat",
        headers=headers,
        json={"query": "where is my order?"}
    )
    
    assert res.status_code == 200
    data = res.json()
    assert "reply" in data
    # Because DummyLLM is used, we expect it to contain 'order'
    assert "order" in data["reply"].lower()

@pytest.mark.asyncio
async def test_bot_product_search_intent(async_client: AsyncClient, registered_user: dict):
    headers = {"Authorization": f"Bearer {registered_user['token']}"}
    
    res = await async_client.post(
        "/api/bot/chat",
        headers=headers,
        json={"query": "I am looking for a laptop"}
    )
    
    assert res.status_code == 200
    data = res.json()
    assert "reply" in data
    # Because DummyLLM is used, it should reply differently
    assert "recommend" in data["reply"].lower()
