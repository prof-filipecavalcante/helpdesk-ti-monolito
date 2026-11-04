from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

Prioridade = Literal["baixa", "media", "alta", "critica"]
Status = Literal["aberto", "em_atendimento", "resolvido", "fechado"]


class ChamadoCriar(BaseModel):
    titulo: str
    descricao: str
    prioridade: Prioridade
    solicitante_id: int
    ativo_id: int | None = None


class Atribuicao(BaseModel):
    tecnico_id: int


class MudancaStatus(BaseModel):
    status: Status


class ComentarioCriar(BaseModel):
    autor_id: int
    texto: str


class ComentarioSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    autor_id: int
    texto: str
    criado_em: datetime


class ChamadoSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: str
    descricao: str
    prioridade: Prioridade
    status: Status
    solicitante_id: int
    tecnico_id: int | None
    ativo_id: int | None
    criado_em: datetime
    prazo_sla: datetime
    comentarios: list[ComentarioSaida] = []


class Painel(BaseModel):
    total: int
    por_status: dict[str, int]
    atrasados: int
