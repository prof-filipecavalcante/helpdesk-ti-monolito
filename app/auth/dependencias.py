"""Dependências do FastAPI para exigir login e perfil."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth import tokens
from app.database import get_db
from app.usuarios.modelos import Usuario

esquema = HTTPBearer(auto_error=False)

NAO_AUTENTICADO = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Faça login para continuar.",
    headers={"WWW-Authenticate": "Bearer"},
)


def usuario_atual(
    credenciais: HTTPAuthorizationCredentials | None = Depends(esquema),
    db: Session = Depends(get_db),
) -> Usuario:
    if credenciais is None or credenciais.scheme.lower() != "bearer":
        raise NAO_AUTENTICADO
    try:
        usuario_id = tokens.ler(credenciais.credentials)
    except tokens.TokenInvalido:
        raise NAO_AUTENTICADO
    usuario = db.get(Usuario, usuario_id)
    if usuario is None or not usuario.ativo:
        raise NAO_AUTENTICADO
    return usuario


def exigir_perfil(*perfis: str):
    """Libera a rota só para os perfis informados."""
    def verificar(usuario: Usuario = Depends(usuario_atual)) -> Usuario:
        if usuario.perfil not in perfis:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não tem permissão para esta ação.")
        return usuario
    return verificar
