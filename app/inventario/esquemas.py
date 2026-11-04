from typing import Literal

from pydantic import BaseModel, ConfigDict

TipoAtivo = Literal["computador", "notebook", "impressora", "rede", "outro"]


class AtivoCriar(BaseModel):
    patrimonio: str
    tipo: TipoAtivo
    descricao: str
    setor: str


class AtivoSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patrimonio: str
    tipo: TipoAtivo
    descricao: str
    setor: str
