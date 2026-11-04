import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture
def cliente(monkeypatch):
    """Cliente de teste com um banco novo, em memória, para cada teste."""
    monkeypatch.setenv("DADOS_EXEMPLO", "0")
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Sessao = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def db_de_teste():
        db = Sessao()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = db_de_teste
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def base(cliente):
    """Cria um solicitante, um técnico e um ativo."""
    sol = cliente.post("/usuarios", json={"nome": "Ana", "email": "ana@x.com", "perfil": "solicitante"}).json()
    tec = cliente.post("/usuarios", json={"nome": "Carla", "email": "carla@x.com", "perfil": "tecnico"}).json()
    ativo = cliente.post("/ativos", json={"patrimonio": "PAT-1", "tipo": "computador", "descricao": "Desktop", "setor": "TI"}).json()
    return {"sol": sol, "tec": tec, "ativo": ativo}
