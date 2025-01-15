import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database import Base
from app.routers.users import get_db
from models import Usuario

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_user():
    db = TestingSessionLocal()
    user = Usuario(username="Test user", email="test@gmail.com", is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.query(Usuario).delete()
    db.commit()
    db.close()


TOKEN = "teste_token"

def test_authorization_missing(client):
    response = client.get("/users/", headers={})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token format. Expected Bearer Auth"}

def test_authorization_invalid(client):
    response = client.get("/users/", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or missing Authorization token"}

def test_create_user(client):
    headers = {"Authorization": f"Bearer {TOKEN}"}
    user_data = {"username": "Nomura", "email": "nomura@gmail.com", "is_active": True}
    response = client.post("/users/", json=user_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "Nomura"
    assert data["email"] == "nomura@gmail.com"
    assert data["is_active"] == True

def test_get_user(client, test_user):
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = client.get(f"/users/{test_user.id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "Test user"
    assert data["email"] == "test@gmail.com"
    assert data["is_active"] == True

def test_get_users(client, test_user):
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = client.get("/users/", headers=headers)
    assert response.status_code == 200
    users = response.json()
    assert len(users) > 0

def test_update_user(client, test_user):
    headers = {"Authorization": f"Bearer {TOKEN}"}
    update_data = {"username": "Teste Updated"}
    response = client.put(f"/users/{test_user.id}", json=update_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "Teste Updated"

def test_delete_user(client, test_user):
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = client.delete(f"/users/{test_user.id}", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": f"User {test_user.id} deleted successfully"}

    response = client.get(f"/users/{test_user.id}", headers=headers)
    assert response.status_code == 404
