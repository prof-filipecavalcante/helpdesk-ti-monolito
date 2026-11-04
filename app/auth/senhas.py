"""Hash de senhas com scrypt (biblioteca padrão do Python).

A senha nunca é guardada: guardamos só o resultado do hash, com um sal aleatório.
"""
import base64
import hashlib
import hmac
import secrets

N, R, P = 2**14, 8, 1
TAMANHO = 32


def _b64(dados: bytes) -> str:
    return base64.b64encode(dados).decode()


def gerar_hash(senha: str) -> str:
    sal = secrets.token_bytes(16)
    resultado = hashlib.scrypt(senha.encode(), salt=sal, n=N, r=R, p=P, dklen=TAMANHO)
    return f"scrypt${N}${R}${P}${_b64(sal)}${_b64(resultado)}"


def conferir(senha: str, hash_guardado: str) -> bool:
    try:
        _, n, r, p, sal, esperado = hash_guardado.split("$")
        resultado = hashlib.scrypt(
            senha.encode(), salt=base64.b64decode(sal), n=int(n), r=int(r), p=int(p), dklen=TAMANHO
        )
    except (ValueError, TypeError):
        return False
    # compare_digest evita descobrir a senha pelo tempo de resposta
    return hmac.compare_digest(resultado, base64.b64decode(esperado))


# Usado quando o e-mail não existe, para que a resposta leve o mesmo tempo
HASH_FALSO = gerar_hash(secrets.token_urlsafe(16))
