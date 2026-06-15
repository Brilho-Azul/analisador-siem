import hashlib
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from main import app, Base, get_db, UsuarioDB


@pytest.fixture(autouse=True)
def db_isolated():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    hashed = hashlib.sha256("admin".encode()).hexdigest()
    db.add(UsuarioDB(username="admin", hashed_password=hashed))
    db.commit()
    db.close()

    def _override():
        sess = TestingSessionLocal()
        try:
            yield sess
        finally:
            sess.close()

    original = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = _override
    yield
    if original is not None:
        app.dependency_overrides[get_db] = original
    else:
        app.dependency_overrides.pop(get_db, None)


client = TestClient(app)


def test_login_success():
    response = client.post("/api/auth/login", json={"username": "admin", "password": "admin"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "admin"
    assert data["message"] == "Login realizado com sucesso"


def test_login_wrong_password():
    response = client.post("/api/auth/login", json={"username": "admin", "password": "senha_errada"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Usuário ou senha inválidos"


def test_login_wrong_user():
    response = client.post("/api/auth/login", json={"username": "inexistente", "password": "admin"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Usuário ou senha inválidos"


def test_login_empty_body():
    response = client.post("/api/auth/login", json={})
    assert response.status_code == 422


def test_login_missing_fields():
    response = client.post("/api/auth/login", json={"username": "admin"})
    assert response.status_code == 422
