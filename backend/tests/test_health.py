def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_login(client):
    response = client.post(
        "/api/auth/login",
        data={"username": "admin@example.com", "password": "secret"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_me_without_token(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_me_with_token(client):
    login = client.post(
        "/api/auth/login",
        data={"username": "admin@example.com", "password": "secret"},
    )
    token = login.json()["access_token"]
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@example.com"
    assert data["roles"] == ["admin"]
