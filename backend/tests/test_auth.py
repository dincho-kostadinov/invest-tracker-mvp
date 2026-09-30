import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _unique_email() -> str:
    return f"test-{uuid.uuid4().hex}@example.com"


def test_signup_creates_user_and_returns_token(cleanup_user: list[str]) -> None:
    email = _unique_email()
    cleanup_user.append(email)

    response = client.post("/auth/signup", json={"email": email, "password": "correcthorse"})

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_signup_rejects_duplicate_email(cleanup_user: list[str]) -> None:
    email = _unique_email()
    cleanup_user.append(email)
    client.post("/auth/signup", json={"email": email, "password": "correcthorse"})

    response = client.post("/auth/signup", json={"email": email, "password": "correcthorse"})

    assert response.status_code == 409


def test_login_succeeds_with_correct_password(cleanup_user: list[str]) -> None:
    email = _unique_email()
    cleanup_user.append(email)
    client.post("/auth/signup", json={"email": email, "password": "correcthorse"})

    response = client.post("/auth/login", json={"email": email, "password": "correcthorse"})

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_rejects_wrong_password(cleanup_user: list[str]) -> None:
    email = _unique_email()
    cleanup_user.append(email)
    client.post("/auth/signup", json={"email": email, "password": "correcthorse"})

    response = client.post("/auth/login", json={"email": email, "password": "wrong-password"})

    assert response.status_code == 401


def test_me_returns_current_user(cleanup_user: list[str]) -> None:
    email = _unique_email()
    cleanup_user.append(email)
    signup = client.post("/auth/signup", json={"email": email, "password": "correcthorse"})
    token = signup.json()["access_token"]

    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["email"] == email


def test_me_rejects_missing_token() -> None:
    response = client.get("/me")

    assert response.status_code == 401


def test_me_rejects_invalid_token() -> None:
    response = client.get("/me", headers={"Authorization": "Bearer not-a-real-token"})

    assert response.status_code == 401


def test_signup_rejects_password_over_72_bytes() -> None:
    # 19 emoji = 19 chars but 76 UTF-8 bytes — under any char-count limit,
    # over bcrypt's byte limit. Must be a clean 422, not a crash.
    email = _unique_email()
    response = client.post("/auth/signup", json={"email": email, "password": "🔒" * 19})

    assert response.status_code == 422


def test_login_with_overlong_password_returns_401_not_500(cleanup_user: list[str]) -> None:
    email = _unique_email()
    cleanup_user.append(email)
    client.post("/auth/signup", json={"email": email, "password": "correcthorse"})

    response = client.post("/auth/login", json={"email": email, "password": "x" * 200})

    assert response.status_code == 401
