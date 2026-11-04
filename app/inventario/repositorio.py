"""Acesso a dados do módulo de inventário (uso interno do módulo)."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.inventario.modelos import Ativo


def salvar(db: Session, ativo: Ativo) -> Ativo:
    db.add(ativo)
    db.commit()
    db.refresh(ativo)
    return ativo


def buscar_por_id(db: Session, ativo_id: int) -> Ativo | None:
    return db.get(Ativo, ativo_id)


def buscar_por_patrimonio(db: Session, patrimonio: str) -> Ativo | None:
    return db.scalar(select(Ativo).where(Ativo.patrimonio == patrimonio))


def listar(db: Session, setor: str | None = None) -> list[Ativo]:
    consulta = select(Ativo).order_by(Ativo.id)
    if setor:
        consulta = consulta.where(Ativo.setor == setor)
    return list(db.scalars(consulta))
