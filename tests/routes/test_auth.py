from unittest import mock
from unittest.mock import Mock

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import select

from src.conf import messages as msg
from src.database.models import User
from tests.conftest import TestingSessionLocal

user_data = {
    "username": "new_user",
    "email": "new_user@example.com",
    "password": "12345678"
}


def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("api/auth/signup", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert user_data["password"] not in data
    assert "avatar" in data
    assert data["confirmed"] is False


def test_signup_with_existing_email(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("api/auth/signup", json=user_data)
    assert response.status_code == status.HTTP_409_CONFLICT, response.text
    assert response.json() == {"detail": msg.ACCOUNT_EXISTS}


def test_login_with_out_confirmed(client):
    response = client.post("api/auth/login", data={"username": user_data["email"], "password": user_data["password"]})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.text
    assert response.json() == {"detail": msg.ACCOUNT_NOT_CONFIRMED}


# @pytest.mark.asyncio
# async def test_login(client, redis_test_client):
#     async with TestingSessionLocal() as session:
#         current_user = await session.execute(select(User).where(User.email == user_data.get("email")))
#         if current_user:
#             current_user.confirmed = True
#             await session.commit()
#             # TODO щоб запрацював тест мені потрібно тут проабдейтити кеш current_user
#             # або по иншому не знаю шо з цим робити
#
#     response = client.post("api/auth/login",
#                            data={"username": user_data.get("email"), "password": user_data.get("password")})
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert "access_token" in data
#     assert "refresh_token" in data
#     assert "token_type" in data
