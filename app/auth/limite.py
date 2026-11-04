"""Limite de tentativas de login (em memória).

Depois de várias senhas erradas para o mesmo e-mail e endereço, o login fica
bloqueado por alguns minutos. Em microsserviços, esse controle precisaria
ficar em um lugar compartilhado (por exemplo, Redis).
"""
import time
from collections import defaultdict
from threading import Lock

from app.config import LOGIN_JANELA_SEGUNDOS, LOGIN_MAX_FALHAS

_falhas: dict[str, list[float]] = defaultdict(list)
_trava = Lock()


def _recentes(chave: str, agora: float) -> list[float]:
    _falhas[chave] = [t for t in _falhas[chave] if agora - t < LOGIN_JANELA_SEGUNDOS]
    return _falhas[chave]


def bloqueado(chave: str) -> bool:
    with _trava:
        return len(_recentes(chave, time.monotonic())) >= LOGIN_MAX_FALHAS


def registrar_falha(chave: str) -> None:
    with _trava:
        agora = time.monotonic()
        _recentes(chave, agora).append(agora)


def limpar(chave: str) -> None:
    with _trava:
        _falhas.pop(chave, None)


def limpar_tudo() -> None:
    with _trava:
        _falhas.clear()
