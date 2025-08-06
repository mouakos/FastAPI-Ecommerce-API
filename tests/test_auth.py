from datetime import timedelta
from app.utils.security import create_token

import pytest
from httpx import AsyncClient, Response
import uuid
from fastapi import status


async def signup_user(
    client: AsyncClient,
    email,
    password,
    firstname="Test",
    lastname="User",
    gender="male",
) -> Response:
    payload = {
        "email": email,
        "password": password,
        "firstname": firstname,
        "lastname": lastname,
        "gender": gender,
    }
    return await client.post("/api/v1/auth/signup", json=payload)


async def login_user(client, email, password):
    payload = {
        "email": email,
        "password": password,
    }
    return await client.post("/api/v1/auth/login", json=payload)


@pytest.mark.asyncio
async def test_signup_success(client: AsyncClient):
    email = f"user_{uuid.uuid4().hex}@example.com"
    password = "StrongPassword123"
    response = await signup_user(client, email, password)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == email
    assert data["firstname"] == "Test"
    assert data["lastname"] == "User"
    assert "id" in data


@pytest.mark.asyncio
async def test_signup_duplicate_email(client: AsyncClient):
    email = f"user_{uuid.uuid4().hex}@example.com"
    password = "StrongPassword123"
    response1 = await signup_user(client, email, password)
    assert response1.status_code == status.HTTP_201_CREATED
    response2 = await signup_user(client, email, password)
    assert response2.status_code in (
        status.HTTP_400_BAD_REQUEST,
        status.HTTP_409_CONFLICT,
    )


@pytest.mark.asyncio
async def test_signup_invalid_data(client: AsyncClient):
    response = await signup_user(
        client,
        email="not-an-email",
        password="123",
        firstname="",
        lastname="",
        gender="unknown",
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    email = f"user_{uuid.uuid4().hex}@example.com"
    password = "StrongPassword123"
    resp = await signup_user(client, email, password)
    assert resp.status_code == status.HTTP_201_CREATED
    response = await login_user(client, email, password)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "Bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    email = f"user_{uuid.uuid4().hex}@example.com"
    password = "StrongPassword123"
    resp = await signup_user(client, email, password)
    assert resp.status_code == status.HTTP_201_CREATED
    response = await login_user(client, email, "WrongPassword")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    email = f"nouser_{uuid.uuid4().hex}@example.com"
    response = await login_user(client, email, "SomePassword123")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient):
    email = f"user_{uuid.uuid4().hex}@example.com"
    password = "StrongPassword123"
    resp = await signup_user(client, email, password)
    assert resp.status_code == status.HTTP_201_CREATED
    login_resp = await login_user(client, email, password)
    assert login_resp.status_code == status.HTTP_200_OK
    tokens = login_resp.json()
    refresh_token = tokens["refresh_token"]
    headers = {"Authorization": f"Bearer {refresh_token}"}
    response = await client.get("/api/v1/auth/refresh", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "Bearer"


@pytest.mark.asyncio
async def test_refresh_with_access_token(client: AsyncClient):
    email = f"user_{uuid.uuid4().hex}@example.com"
    password = "StrongPassword123"
    resp = await signup_user(client, email, password)
    assert resp.status_code == status.HTTP_201_CREATED
    login_resp = await login_user(client, email, password)
    assert login_resp.status_code == status.HTTP_200_OK
    tokens = login_resp.json()
    access_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.get("/api/v1/auth/refresh", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_refresh_with_invalid_token(client: AsyncClient):
    invalid_token = "this.is.not.a.valid.token"
    headers = {"Authorization": f"Bearer {invalid_token}"}
    response = await client.get("/api/v1/auth/refresh", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_refresh_with_expired_token(client: AsyncClient):
    expired_token = create_token(
        user_id="2",
        user_role="customer",
        expires_delta=timedelta(seconds=-10),
        refresh=True,
    )
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = await client.get("/api/v1/auth/refresh", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_access_with_refresh_token(client: AsyncClient):
    email = f"user_{uuid.uuid4().hex}@example.com"
    password = "StrongPassword123"
    resp = await signup_user(client, email, password)
    assert resp.status_code == status.HTTP_201_CREATED
    login_resp = await login_user(client, email, password)
    assert login_resp.status_code == status.HTTP_200_OK
    tokens = login_resp.json()
    refresh_token = tokens["refresh_token"]
    headers = {"Authorization": f"Bearer {refresh_token}"}
    response = await client.get("/api/v1/users/me/", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
