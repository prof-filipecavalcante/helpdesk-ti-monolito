"""HelpDesk TI (monólito).

Uma única aplicação, um único banco e uma única implantação.
Os módulos ficam em pastas separadas e conversam pela porta pública
de cada um (`servico.py`).
"""
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.exc import IntegrityError

from app import dados_exemplo
from app.auth.rotas import router as auth_router
from app.chamados.rotas import router as chamados_router
from app.config import DOCS_ATIVA
from app.database import Base, SessionLocal, engine
from app.erros import NaoEncontrado, RegraDeNegocio, SemPermissao
from app.inventario.rotas import router as inventario_router
from app.notificacoes.rotas import router as notificacoes_router
from app.seguranca_http import CabecalhosDeSeguranca
from app.usuarios.rotas import router as usuarios_router

WEB = Path(__file__).parent / "web"


@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    """Cria as tabelas e, se pedido, os dados de exemplo ao iniciar."""
    Base.metadata.create_all(engine)
    if os.getenv("DADOS_EXEMPLO", "1") == "1":
        with SessionLocal() as db:
            dados_exemplo.carregar(db)
    yield


app = FastAPI(
    title="HelpDesk TI (monólito)", version="2.0.0", lifespan=ciclo_de_vida,
    docs_url="/docs" if DOCS_ATIVA else None, redoc_url=None,
    openapi_url="/openapi.json" if DOCS_ATIVA else None,
)
app.add_middleware(CabecalhosDeSeguranca)

app.include_router(auth_router)
app.include_router(usuarios_router)
app.include_router(inventario_router)
app.include_router(chamados_router)
app.include_router(notificacoes_router)


@app.exception_handler(NaoEncontrado)
def tratar_nao_encontrado(request: Request, erro: NaoEncontrado):
    return JSONResponse(status_code=404, content={"detail": str(erro)})


@app.exception_handler(RegraDeNegocio)
def tratar_regra(request: Request, erro: RegraDeNegocio):
    return JSONResponse(status_code=422, content={"detail": str(erro)})


@app.exception_handler(SemPermissao)
def tratar_sem_permissao(request: Request, erro: SemPermissao):
    return JSONResponse(status_code=403, content={"detail": str(erro)})


@app.exception_handler(IntegrityError)
def tratar_conflito(request: Request, erro: IntegrityError):
    # Não expõe detalhes do banco na resposta
    return JSONResponse(status_code=409, content={"detail": "O registro conflita com outro já existente."})


@app.get("/saude", tags=["Saúde"])
def saude():
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def tela_inicial():
    return FileResponse(WEB / "index.html")


@app.get("/app.js", include_in_schema=False)
def script():
    return FileResponse(WEB / "app.js", media_type="text/javascript")


@app.get("/estilo.css", include_in_schema=False)
def estilo():
    return FileResponse(WEB / "estilo.css", media_type="text/css")
