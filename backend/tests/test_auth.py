import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_register_and_login(async_client: AsyncClient):
    unique_suffix = uuid.uuid4().hex[:6]
    email = f"testuser_{unique_suffix}@example.com"
    password = "secretpassword123"

    # 1. Register a new user
    user_payload = {
        "email": email,
        "password": password
    }
    
    response = await async_client.post("/api/auth/register", json=user_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email
    assert "id" in data
    assert "customer" in data["roles"]

    # 2. Login
    login_payload = {
        "username": email,
        "password": password
    }
    # OAuth2PasswordRequestForm requires form data
    response = await async_client.post("/api/auth/login", data=login_payload)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    access_token = token_data["access_token"]

    # 3. Get Me
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await async_client.get("/api/auth/me", headers=headers)
    assert response.status_code == 200
    me_data = response.json()
    assert me_data["email"] == email

    # 4. Failed Login
    bad_login_payload = {
        "username": email,
        "password": "wrongpassword"
    }
    response = await async_client.post("/api/auth/login", data=bad_login_payload)
    assert response.status_code == 401
