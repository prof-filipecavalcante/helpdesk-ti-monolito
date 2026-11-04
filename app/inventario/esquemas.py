from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

TipoAtivo = Literal["computador", "notebook", "impressora", "rede", "outro"]


class AtivoCriar(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    patrimonio: str = Field(min_length=3, max_length=30, pattern=r"^[A-Za-z0-9-]+$")
    tipo: TipoAtivo
    descricao: str = Field(min_length=2, max_length=200)
    setor: str = Field(min_length=2, max_length=80)


class AtivoSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patrimonio: str
    tipo: TipoAtivo
    descricao: str
    setor: str
