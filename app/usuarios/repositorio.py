"""Acesso a dados do módulo de usuários (uso interno do módulo)."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.usuarios.modelos import Usuario


def salvar(db: Session, usuario: Usuario) -> Usuario:
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def buscar_por_id(db: Session, usuario_id: int) -> Usuario | None:
    return db.get(Usuario, usuario_id)


def buscar_por_email(db: Session, email: str) -> Usuario | None:
    return db.scalar(select(Usuario).where(Usuario.email == email))


def listar(db: Session, perfil: str | None = None) -> list[Usuario]:
    consulta = select(Usuario).order_by(Usuario.id)
    if perfil:
        consulta = consulta.where(Usuario.perfil == perfil)
    return list(db.scalars(consulta))
