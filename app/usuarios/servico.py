"""Regras do módulo de usuários. É a porta pública do módulo."""
from sqlalchemy.orm import Session

from app.auth import senhas
from app.erros import NaoEncontrado, RegraDeNegocio
from app.usuarios import repositorio
from app.usuarios.esquemas import UsuarioCriar
from app.usuarios.modelos import Usuario


def criar(db: Session, dados: UsuarioCriar) -> Usuario:
    email = dados.email.lower()
    if repositorio.buscar_por_email(db, email):
        raise RegraDeNegocio("Já existe um usuário com este e-mail.")
    usuario = Usuario(nome=dados.nome, email=email, perfil=dados.perfil, senha_hash=senhas.gerar_hash(dados.senha))
    return repositorio.salvar(db, usuario)


def buscar_por_email(db: Session, email: str) -> Usuario | None:
    return repositorio.buscar_por_email(db, email.lower())


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
