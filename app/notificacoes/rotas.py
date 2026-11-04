from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.notificacoes import servico
from app.notificacoes.esquemas import NotificacaoSaida

router = APIRouter(prefix="/notificacoes", tags=["Notificações"])


@router.get("", response_model=list[NotificacaoSaida])
def listar_notificacoes(destinatario_id: int | None = None, db: Session = Depends(get_db)):
    return servico.listar(db, destinatario_id)
