"""Testes de segurança: autenticação, permissões e validação de entrada."""
from datetime import datetime, timedelta, timezone

import jwt

from app import config
from tests.conftest import SENHA


def abrir(cliente, h, **extra):
    return cliente.post("/chamados", headers=h, json={"titulo": "Teste", "descricao": "Teste", "prioridade": "baixa", **extra})


# ---------- autenticação ----------

def test_rotas_exigem_login(cliente, contas):
    for metodo, rota in [("get", "/chamados"), ("get", "/usuarios"), ("get", "/ativos"), ("get", "/notificacoes"),
                         ("post", "/chamados"), ("get", "/auth/eu")]:
        assert getattr(cliente, metodo)(rota).status_code == 401, rota


def test_login_com_senha_errada(cliente, contas):
    r = cliente.post("/auth/login", json={"email": "ana@x.com", "senha": "errada123"})
    assert r.status_code == 401 and r.json()["detail"] == "E-mail ou senha inválidos."


def test_login_com_email_inexistente_tem_a_mesma_mensagem(cliente, contas):
    r = cliente.post("/auth/login", json={"email": "ninguem@x.com", "senha": "errada123"})
    assert r.status_code == 401 and r.json()["detail"] == "E-mail ou senha inválidos."


def test_bloqueio_apos_varias_senhas_erradas(cliente, contas):
    for _ in range(config.LOGIN_MAX_FALHAS):
        cliente.post("/auth/login", json={"email": "ana@x.com", "senha": "errada123"})
    # mesmo com a senha certa, fica bloqueado por um tempo
    assert cliente.post("/auth/login", json={"email": "ana@x.com", "senha": SENHA}).status_code == 429


def test_token_adulterado(cliente, contas):
    token = contas["ana"]["headers"]["Authorization"] + "x"
    assert cliente.get("/auth/eu", headers={"Authorization": token}).status_code == 401


def test_token_assinado_com_outro_segredo(cliente, contas):
    falso = jwt.encode({"sub": str(contas["admin"]["id"]), "iss": config.JWT_EMISSOR,
                        "iat": datetime.now(timezone.utc), "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
                       "segredo-de-outra-pessoa-com-mais-de-32-caracteres", algorithm="HS256")
    assert cliente.get("/auth/eu", headers={"Authorization": f"Bearer {falso}"}).status_code == 401


def test_token_sem_assinatura_alg_none(cliente, contas):
    falso = jwt.encode({"sub": str(contas["admin"]["id"]), "iss": config.JWT_EMISSOR,
                        "iat": datetime.now(timezone.utc), "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
                       None, algorithm="none")
    assert cliente.get("/auth/eu", headers={"Authorization": f"Bearer {falso}"}).status_code == 401


def test_token_expirado(cliente, contas):
    antigo = datetime.now(timezone.utc) - timedelta(hours=2)
    vencido = jwt.encode({"sub": str(contas["ana"]["id"]), "iss": config.JWT_EMISSOR, "iat": antigo,
                          "exp": antigo + timedelta(minutes=5)}, config.JWT_SEGREDO, algorithm="HS256")
    assert cliente.get("/auth/eu", headers={"Authorization": f"Bearer {vencido}"}).status_code == 401


def test_senha_guardada_com_hash(sessao, contas):
    from app.usuarios.modelos import Usuario
    with sessao() as db:
        u = db.query(Usuario).filter_by(email="ana@x.com").one()
        assert SENHA not in u.senha_hash and u.senha_hash.startswith("scrypt$")


def test_senha_fraca_e_recusada(cliente, contas):
    r = cliente.post("/usuarios", headers=contas["admin"]["headers"],
                     json={"nome": "Eva", "email": "eva@x.com", "perfil": "solicitante", "senha": "abcdefgh"})
    assert r.status_code == 422


# ---------- permissões ----------

def test_solicitante_nao_cria_usuario(cliente, contas):
    r = cliente.post("/usuarios", headers=contas["ana"]["headers"],
                     json={"nome": "Eva", "email": "eva@x.com", "perfil": "admin", "senha": "Forte1234"})
    assert r.status_code == 403


def test_solicitante_nao_cadastra_ativo(cliente, contas):
    r = cliente.post("/ativos", headers=contas["ana"]["headers"],
                     json={"patrimonio": "PAT-9", "tipo": "outro", "descricao": "X", "setor": "TI"})
    assert r.status_code == 403


def test_solicitante_nao_ve_chamado_de_outra_pessoa(cliente, contas):
    cid = abrir(cliente, contas["ana"]["headers"]).json()["id"]
    assert cliente.get(f"/chamados/{cid}", headers=contas["bia"]["headers"]).status_code == 404
    assert cliente.get("/chamados", headers=contas["bia"]["headers"]).json() == []


def test_solicitante_nao_atribui_nem_resolve(cliente, contas):
    cid = abrir(cliente, contas["ana"]["headers"]).json()["id"]
    h = contas["ana"]["headers"]
    assert cliente.patch(f"/chamados/{cid}/atribuir", headers=h, json={"tecnico_id": contas["carla"]["id"]}).status_code == 403
    assert cliente.patch(f"/chamados/{cid}/status", headers=h, json={"status": "em_atendimento"}).status_code == 403


def test_nao_da_para_abrir_chamado_em_nome_de_outro(cliente, contas):
    r = abrir(cliente, contas["ana"]["headers"], solicitante_id=contas["bia"]["id"])
    assert r.status_code == 422  # campo extra é recusado


def test_nao_da_para_comentar_em_nome_de_outro(cliente, contas):
    cid = abrir(cliente, contas["ana"]["headers"]).json()["id"]
    r = cliente.post(f"/chamados/{cid}/comentarios", headers=contas["ana"]["headers"],
                     json={"texto": "oi", "autor_id": contas["carla"]["id"]})
    assert r.status_code == 422


def test_notificacoes_sao_so_do_proprio_usuario(cliente, contas):
    abrir(cliente, contas["ana"]["headers"])
    assert cliente.get("/notificacoes", headers=contas["bia"]["headers"]).json() == []


# ---------- entrada e respostas ----------

def test_titulo_grande_demais(cliente, contas):
    assert abrir(cliente, contas["ana"]["headers"], titulo="x" * 500).status_code == 422


def test_requisicao_grande_demais(cliente, contas):
    corpo = '{"titulo": "' + "x" * 70000 + '"}'
    r = cliente.post("/chamados", headers={**contas["ana"]["headers"], "Content-Type": "application/json"}, content=corpo)
    assert r.status_code == 413


def test_texto_com_html_e_guardado_como_texto(cliente, contas):
    r = abrir(cliente, contas["ana"]["headers"], titulo="<script>alert(1)</script>")
    assert r.status_code == 201 and r.json()["titulo"] == "<script>alert(1)</script>"


def test_tela_escapa_o_html():
    from pathlib import Path
    js = (Path(__file__).parent.parent / "app" / "web" / "app.js").read_text()
    assert "const esc =" in js and "onclick" not in js


def test_cabecalhos_de_seguranca(cliente):
    r = cliente.get("/")
    assert "script-src 'self'" in r.headers["content-security-policy"]
    assert r.headers["x-content-type-options"] == "nosniff"
    assert r.headers["x-frame-options"] == "DENY"
