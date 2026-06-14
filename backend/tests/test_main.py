import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from main import app, Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# Dependency override
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_crud_lifecycle():
    # 1. Listar inicialmente vazio
    response = client.get("/api/produtos")
    assert response.status_code == 200
    assert response.json() == []

    # 2. Criar produto
    novo_produto = {"nome": "Teclado Mecânico", "preco": 350.0, "descricao": "Teclado RGB"}
    response = client.post("/api/produtos", json=novo_produto)
    assert response.status_code == 201
    dados_criados = response.json()
    assert dados_criados["id"] == 1
    assert dados_criados["nome"] == "Teclado Mecânico"

    # 3. Ler o produto criado
    response = client.get("/api/produtos/1")
    assert response.status_code == 200
    assert response.json() == dados_criados

    # 4. Atualizar o produto
    produto_atualizado = {"nome": "Teclado Mecânico Pro", "preco": 399.90, "descricao": "Teclado RGB Switch Blue"}
    response = client.put("/api/produtos/1", json=produto_atualizado)
    assert response.status_code == 200
    dados_atualizados = response.json()
    assert dados_atualizados["nome"] == "Teclado Mecânico Pro"
    assert dados_atualizados["preco"] == 399.90

    # 5. Ler novamente e confirmar alteração
    response = client.get("/api/produtos/1")
    assert response.json()["nome"] == "Teclado Mecânico Pro"

    # 6. Deletar o produto
    response = client.delete("/api/produtos/1")
    assert response.status_code == 200
    assert response.json() == {"message": "Produto deletado com sucesso"}

    # 7. Tentar obter deletado (404)
    response = client.get("/api/produtos/1")
    assert response.status_code == 404
