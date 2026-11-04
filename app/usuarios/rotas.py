from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencias import exigir_perfil, usuario_atual
from app.database import get_db
from app.usuarios import servico
from app.usuarios.esquemas import Perfil, UsuarioCriar, UsuarioPublico, UsuarioSaida

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.post("", response_model=UsuarioSaida, status_code=201, dependencies=[Depends(exigir_perfil("admin"))])
def criar_usuario(dados: UsuarioCriar, db: Session = Depends(get_db)):
    return servico.criar(db, dados)


@router.get("", response_model=list[UsuarioPublico], dependencies=[Depends(usuario_atual)])
def listar_usuarios(perfil: Perfil | None = None, db: Session = Depends(get_db)):
    return servico.listar(db, perfil)


@router.get("/{usuario_id}", response_model=UsuarioPublico, dependencies=[Depends(usuario_atual)])
def obter_usuario(usuario_id: int, db: Session = Depends(get_db)):
    return servico.obter(db, usuario_id)
