import bcrypt
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.models import User
from app.auth.security import decode_access_token


def register_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "name": "Ada Lovelace",
        "email": "ada@example.com",
        "password": "secret123",
    }
    payload.update(overrides)
    return payload


def test_register_returns_user_and_hashes_password(
    client: TestClient, db_session: Session
) -> None:
    # Arrange
    payload = register_payload(email="  Ada@Example.COM ")

    # Act
    response = client.post("/auth/register", json=payload)

    # Assert
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "ada@example.com"
    assert body["role"] == "user"
    assert "password" not in body

    user = db_session.scalar(select(User).where(User.email == "ada@example.com"))
    assert user is not None
    assert user.password_hash != "secret123"
    assert user.password_hash.startswith("$2b$12$")
    assert bcrypt.checkpw(b"secret123", user.password_hash.encode("ascii"))


def test_register_duplicate_email_returns_conflict(client: TestClient) -> None:
    # Arrange
    client.post("/auth/register", json=register_payload())

    # Act
    response = client.post("/auth/register", json=register_payload())

    # Assert
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "EMAIL_ALREADY_REGISTERED"


def test_register_invalid_email_returns_validation_error(
    client: TestClient,
) -> None:
    # Act
    response = client.post(
        "/auth/register", json=register_payload(email="sin-arroba")
    )

    # Assert
    assert response.status_code == 422


def test_register_short_password_returns_validation_error(
    client: TestClient,
) -> None:
    # Act
    response = client.post(
        "/auth/register", json=register_payload(password="corta")
    )

    # Assert
    assert response.status_code == 422


def test_login_returns_bearer_token_for_valid_credentials(
    client: TestClient,
) -> None:
    # Arrange
    client.post("/auth/register", json=register_payload())

    # Act
    response = client.post(
        "/auth/login",
        json={"email": "ada@example.com", "password": "secret123"},
    )

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == "ada@example.com"
    payload = decode_access_token(body["access_token"])
    assert payload.role == "user"


def test_login_wrong_password_returns_unauthorized(
    client: TestClient,
) -> None:
    # Arrange
    client.post("/auth/register", json=register_payload())

    # Act
    response = client.post(
        "/auth/login",
        json={"email": "ada@example.com", "password": "incorrecta"},
    )

    # Assert
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "INVALID_CREDENTIALS"


def test_login_unknown_email_returns_unauthorized(
    client: TestClient,
) -> None:
    # Act
    response = client.post(
        "/auth/login",
        json={"email": "nadie@example.com", "password": "secret123"},
    )

    # Assert
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "INVALID_CREDENTIALS"


def test_me_without_token_returns_unauthorized(client: TestClient) -> None:
    # Act
    response = client.get("/auth/me")

    # Assert
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "AUTH_001"


def test_me_with_invalid_token_returns_unauthorized(
    client: TestClient,
) -> None:
    # Act
    response = client.get(
        "/auth/me", headers={"Authorization": "Bearer token-invalido"}
    )

    # Assert
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "AUTH_001"


def test_me_with_valid_token_returns_current_user(
    client: TestClient,
) -> None:
    # Arrange
    client.post("/auth/register", json=register_payload())
    login = client.post(
        "/auth/login",
        json={"email": "ada@example.com", "password": "secret123"},
    )
    token = login.json()["access_token"]

    # Act
    response = client.get(
        "/auth/me", headers={"Authorization": f"Bearer {token}"}
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["email"] == "ada@example.com"
