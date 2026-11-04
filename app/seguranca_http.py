"""Proteções aplicadas a todas as respostas HTTP."""
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import TAMANHO_MAXIMO_REQUISICAO

# A tela só carrega arquivos do próprio servidor (bloqueia scripts injetados)
CSP_TELA = (
    "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
    "connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
)
# A documentação (Swagger) carrega arquivos de um CDN
CSP_DOCS = (
    "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
    "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; img-src 'self' data: https://fastapi.tiangolo.com; "
    "frame-ancestors 'none'; base-uri 'none'"
)


class CabecalhosDeSeguranca(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        tamanho = request.headers.get("content-length")
        if tamanho and (not tamanho.isdigit() or int(tamanho) > TAMANHO_MAXIMO_REQUISICAO):
            return JSONResponse(status_code=413, content={"detail": "Requisição grande demais."})

        resposta = await call_next(request)
        documentacao = request.url.path in ("/docs", "/redoc", "/openapi.json")
        resposta.headers["Content-Security-Policy"] = CSP_DOCS if documentacao else CSP_TELA
        resposta.headers["X-Content-Type-Options"] = "nosniff"
        resposta.headers["X-Frame-Options"] = "DENY"
        resposta.headers["Referrer-Policy"] = "no-referrer"
        resposta.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        resposta.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        if request.headers.get("authorization"):
            resposta.headers["Cache-Control"] = "no-store"
        return resposta
