from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr

Perfil = Literal["solicitante", "tecnico"]


class UsuarioCriar(BaseModel):
    nome: str
    email: EmailStr
    perfil: Perfil


class UsuarioSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email: str
    perfil: Perfil
