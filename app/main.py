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

from app import dados_exemplo
from app.chamados.rotas import router as chamados_router
from app.database import Base, SessionLocal, engine
from app.erros import NaoEncontrado, RegraDeNegocio
from app.inventario.rotas import router as inventario_router
from app.notificacoes.rotas import router as notificacoes_router
from app.usuarios.rotas import router as usuarios_router


@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    """Cria as tabelas e, se pedido, os dados de exemplo ao iniciar."""
    Base.metadata.create_all(engine)
    if os.getenv("DADOS_EXEMPLO", "1") == "1":
        with SessionLocal() as db:
            dados_exemplo.carregar(db)
    yield


app = FastAPI(title="HelpDesk TI (monólito)", version="1.0.0", lifespan=ciclo_de_vida)

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


@app.get("/saude", tags=["Saúde"])
def saude():
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def tela_inicial():
    """Tela simples do HelpDesk, que usa a própria API."""
    return FileResponse(Path(__file__).parent / "web" / "index.html")
