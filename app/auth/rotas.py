from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy.orm import Session

from app.auth import limite, senhas, tokens
from app.auth.dependencias import usuario_atual
from app.database import get_db
from app.usuarios import servico as usuarios
from app.usuarios.esquemas import UsuarioSaida
from app.usuarios.modelos import Usuario

router = APIRouter(prefix="/auth", tags=["Autenticação"])


class Login(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    senha: str = Field(min_length=1, max_length=128)


class TokenSaida(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expira_em: datetime
    usuario: UsuarioSaida


@router.post("/login", response_model=TokenSaida)
def login(dados: Login, request: Request, db: Session = Depends(get_db)):
    email = dados.email.lower()
    chave = f"{email}|{request.client.host if request.client else '-'}"
    if limite.bloqueado(chave):
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Muitas tentativas. Tente de novo em alguns minutos.")

    usuario = usuarios.buscar_por_email(db, email)
    # Confere a senha mesmo sem usuário, para o tempo de resposta não revelar se o e-mail existe
    senha_ok = senhas.conferir(dados.senha, usuario.senha_hash if usuario else senhas.HASH_FALSO)
    if not usuario or not senha_ok or not usuario.ativo:
        limite.registrar_falha(chave)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "E-mail ou senha inválidos.")

    limite.limpar(chave)
    token, expira = tokens.criar(usuario.id, usuario.perfil)
    return TokenSaida(access_token=token, expira_em=expira, usuario=UsuarioSaida.model_validate(usuario))


@router.get("/eu", response_model=UsuarioSaida)
def quem_sou_eu(usuario: Usuario = Depends(usuario_atual)):
    return usuario
