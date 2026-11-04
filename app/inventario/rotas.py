from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.inventario import servico
from app.inventario.esquemas import AtivoCriar, AtivoSaida

router = APIRouter(prefix="/ativos", tags=["Inventário"])


@router.post("", response_model=AtivoSaida, status_code=201)
def criar_ativo(dados: AtivoCriar, db: Session = Depends(get_db)):
    return servico.criar(db, dados)


@router.get("", response_model=list[AtivoSaida])
def listar_ativos(setor: str | None = None, db: Session = Depends(get_db)):
    return servico.listar(db, setor)


@router.get("/{ativo_id}", response_model=AtivoSaida)
def obter_ativo(ativo_id: int, db: Session = Depends(get_db)):
    return servico.obter(db, ativo_id)
