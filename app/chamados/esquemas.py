from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Prioridade = Literal["baixa", "media", "alta", "critica"]
Status = Literal["aberto", "em_atendimento", "resolvido", "fechado"]


ENTRADA = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ChamadoCriar(BaseModel):
    """O solicitante é sempre o usuário logado: não vem no corpo da requisição."""
    model_config = ENTRADA

    titulo: str = Field(min_length=3, max_length=120)
    descricao: str = Field(min_length=3, max_length=2000)
    prioridade: Prioridade
    ativo_id: int | None = Field(default=None, gt=0)


class Atribuicao(BaseModel):
    model_config = ENTRADA
    tecnico_id: int = Field(gt=0)


class MudancaStatus(BaseModel):
    model_config = ENTRADA
    status: Status


class ComentarioCriar(BaseModel):
    """O autor é sempre o usuário logado."""
    model_config = ENTRADA
    texto: str = Field(min_length=1, max_length=2000)


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
