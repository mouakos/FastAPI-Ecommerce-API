import pytest
from httpx import AsyncClient
from fastapi import status
import uuid


@pytest.mark.asyncio
async def get_access_token(client: AsyncClient):
    email = f"user_{uuid.uuid4().hex}@example.com"
    password = "StrongPassword123"
    signup_payload = {
        "email": email,
        "password": password,
        "firstname": "Test",
        "lastname": "User",
        "gender": "male",
    }
    resp = await client.post("/api/v1/auth/signup", json=signup_payload)
    assert resp.status_code == status.HTTP_201_CREATED
    login_payload = {"email": email, "password": password}
    login_resp = await client.post("/api/v1/auth/login", json=login_payload)
    assert login_resp.status_code == status.HTTP_200_OK
    tokens = login_resp.json()
    return tokens["access_token"], email, password


@pytest.mark.asyncio
async def test_get_my_account(client: AsyncClient):
    access_token, _, _ = await get_access_token(client)
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.get("/api/v1/users/me/", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "email" in data
    assert "id" in data


@pytest.mark.asyncio
async def test_update_my_account(client: AsyncClient):
    access_token, _, _ = await get_access_token(client)
    headers = {"Authorization": f"Bearer {access_token}"}
    update_payload = {"firstname": "Updated", "lastname": "User"}
    response = await client.patch(
        "/api/v1/users/me/", json=update_payload, headers=headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["firstname"] == "Updated"
    assert data["lastname"] == "User"


@pytest.mark.asyncio
async def test_update_my_password(client: AsyncClient):
    access_token, email, old_password = await get_access_token(client)
    headers = {"Authorization": f"Bearer {access_token}"}
    new_password = "NewStrongPassword123"
    password_payload = {
        "current_password": old_password,
        "new_password": new_password,
        "new_password_confirm": new_password,
    }
    response = await client.patch(
        "/api/v1/users/me/update-password", json=password_payload, headers=headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    # Try to login with new password
    login_payload = {"email": email, "password": new_password}
    login_resp = await client.post("/api/v1/auth/login", json=login_payload)
    assert login_resp.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_delete_my_account(client: AsyncClient):
    access_token, email, password = await get_access_token(client)
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.delete("/api/v1/users/me/", headers=headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    # Try to login after deletion
    login_payload = {"email": email, "password": password}
    login_resp = await client.post("/api/v1/auth/login", json=login_payload)
    assert login_resp.status_code == status.HTTP_401_UNAUTHORIZED
