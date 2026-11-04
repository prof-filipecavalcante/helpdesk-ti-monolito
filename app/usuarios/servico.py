"""Regras do módulo de usuários. É a porta pública do módulo."""
from sqlalchemy.orm import Session

from app.erros import NaoEncontrado, RegraDeNegocio
from app.usuarios import repositorio
from app.usuarios.esquemas import UsuarioCriar
from app.usuarios.modelos import Usuario


def criar(db: Session, dados: UsuarioCriar) -> Usuario:
    if repositorio.buscar_por_email(db, dados.email):
        raise RegraDeNegocio("Já existe um usuário com este e-mail.")
    return repositorio.salvar(db, Usuario(**dados.model_dump()))


def obter(db: Session, usuario_id: int) -> Usuario:
    usuario = repositorio.buscar_por_id(db, usuario_id)
    if usuario is None:
        raise NaoEncontrado(f"Usuário {usuario_id} não encontrado.")
    return usuario


def obter_tecnico(db: Session, usuario_id: int) -> Usuario:
    usuario = obter(db, usuario_id)
    if usuario.perfil != "tecnico":
        raise RegraDeNegocio(f"Usuário {usuario_id} não é técnico.")
    return usuario


def listar(db: Session, perfil: str | None = None) -> list[Usuario]:
    return repositorio.listar(db, perfil)
