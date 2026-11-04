import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import limite
from app.database import Base, get_db
from app.main import app
from app.usuarios import servico as usuarios
from app.usuarios.esquemas import UsuarioCriar

SENHA = "Senha123"


@pytest.fixture
def sessao(monkeypatch):
    """Banco novo, em memória, para cada teste."""
    monkeypatch.setenv("DADOS_EXEMPLO", "0")
    limite.limpar_tudo()
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
    yield Sessao
    app.dependency_overrides.clear()


@pytest.fixture
def cliente(sessao):
    with TestClient(app) as c:
        yield c


@pytest.fixture
def contas(sessao, cliente):
    """Cria um admin, dois solicitantes e um técnico, e devolve o cabeçalho de login de cada um."""
    with sessao() as db:
        for nome, email, perfil in [("Admin", "admin@x.com", "admin"), ("Ana", "ana@x.com", "solicitante"),
                                    ("Bia", "bia@x.com", "solicitante"), ("Carla", "carla@x.com", "tecnico")]:
            usuarios.criar(db, UsuarioCriar(nome=nome, email=email, perfil=perfil, senha=SENHA))
    resultado = {}
    for apelido in ("admin", "ana", "bia", "carla"):
        r = cliente.post("/auth/login", json={"email": f"{apelido}@x.com", "senha": SENHA}).json()
        resultado[apelido] = {"headers": {"Authorization": f"Bearer {r['access_token']}"}, "id": r["usuario"]["id"]}
    return resultado


@pytest.fixture
def ativo(cliente, contas):
    return cliente.post("/ativos", headers=contas["carla"]["headers"],
                        json={"patrimonio": "PAT-1", "tipo": "computador", "descricao": "Desktop", "setor": "TI"}).json()
