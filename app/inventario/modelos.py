from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Ativo(Base):
    __tablename__ = "ativos"

    id: Mapped[int] = mapped_column(primary_key=True)
    patrimonio: Mapped[str] = mapped_column(String(30), unique=True)
    tipo: Mapped[str] = mapped_column(String(30))
    descricao: Mapped[str] = mapped_column(String(200))
    setor: Mapped[str] = mapped_column(String(80))
