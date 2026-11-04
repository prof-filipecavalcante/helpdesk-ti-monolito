import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

Perfil = Literal["solicitante", "tecnico", "admin"]


class UsuarioCriar(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    nome: str = Field(min_length=2, max_length=120)
    email: EmailStr
    perfil: Perfil
    senha: str = Field(min_length=8, max_length=128)

    @field_validator("senha")
    @classmethod
    def senha_forte(cls, senha: str) -> str:
        if not (re.search(r"[A-Za-z]", senha) and re.search(r"\d", senha)):
            raise ValueError("A senha precisa ter letras e números.")
        return senha


class UsuarioSaida(BaseModel):
    """Dados completos: só para o próprio usuário, técnicos e administradores."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email: str
    perfil: Perfil


class UsuarioPublico(BaseModel):
    """Dados que qualquer usuário logado pode ver (sem e-mail)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    perfil: Perfil
