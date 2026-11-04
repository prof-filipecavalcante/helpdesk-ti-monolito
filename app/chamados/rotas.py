from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.chamados import servico
from app.chamados.esquemas import (
    Atribuicao, ChamadoCriar, ChamadoSaida, ComentarioCriar, ComentarioSaida, MudancaStatus, Painel, Status,
)
from app.database import get_db

router = APIRouter(prefix="/chamados", tags=["Chamados"])


@router.post("", response_model=ChamadoSaida, status_code=201)
def abrir_chamado(dados: ChamadoCriar, db: Session = Depends(get_db)):
    return servico.abrir(db, dados)


@router.get("", response_model=list[ChamadoSaida])
def listar_chamados(status: Status | None = None, tecnico_id: int | None = None, db: Session = Depends(get_db)):
    return servico.listar(db, status, tecnico_id)


@router.get("/painel", response_model=Painel)
def painel(db: Session = Depends(get_db)):
    return servico.painel(db)


@router.get("/{chamado_id}", response_model=ChamadoSaida)
def obter_chamado(chamado_id: int, db: Session = Depends(get_db)):
    return servico.obter(db, chamado_id)


@router.patch("/{chamado_id}/atribuir", response_model=ChamadoSaida)
def atribuir_chamado(chamado_id: int, dados: Atribuicao, db: Session = Depends(get_db)):
    return servico.atribuir(db, chamado_id, dados.tecnico_id)


@router.patch("/{chamado_id}/status", response_model=ChamadoSaida)
def mudar_status(chamado_id: int, dados: MudancaStatus, db: Session = Depends(get_db)):
    return servico.mudar_status(db, chamado_id, dados.status)


@router.post("/{chamado_id}/comentarios", response_model=ComentarioSaida, status_code=201)
def comentar(chamado_id: int, dados: ComentarioCriar, db: Session = Depends(get_db)):
    return servico.comentar(db, chamado_id, dados)
