import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_seller_profile(async_client: AsyncClient):
    unique_suffix = uuid.uuid4().hex[:6]
    email = f"seller_{unique_suffix}@example.com"
    password = "secretpassword123"

    # 1. Register a new user
    user_payload = {
        "email": email,
        "password": password
    }
    response = await async_client.post("/api/auth/register", json=user_payload)
    assert response.status_code == 200

    # 2. Login to get token
    login_payload = {
        "username": email,
        "password": password
    }
    response = await async_client.post("/api/auth/login", data=login_payload)
    assert response.status_code == 200
    access_token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 3. Apply to be a seller
    seller_payload = {
        "company_name": f"Acme Corp {unique_suffix}"
    }
    response = await async_client.post("/api/sellers/apply", json=seller_payload, headers=headers)
    assert response.status_code == 200
    seller_data = response.json()
    assert seller_data["company_name"] == f"Acme Corp {unique_suffix}"
    assert "id" in seller_data

    # 4. Check 'me' endpoint with seller role
    response = await async_client.get("/api/sellers/me", headers=headers)
    assert response.status_code == 200
    me_data = response.json()
    assert me_data["id"] == seller_data["id"]

    # 5. Get Me (Auth) should now show 'seller' role
    response = await async_client.get("/api/auth/me", headers=headers)
    assert response.status_code == 200
    auth_data = response.json()
    assert "seller" in auth_data["roles"]

    # 6. Apply again should fail
    response = await async_client.post("/api/sellers/apply", json=seller_payload, headers=headers)
    assert response.status_code == 400
