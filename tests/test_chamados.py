from datetime import datetime


def abrir(cliente, base, prioridade="alta", **extra):
    dados = {"titulo": "PC não liga", "descricao": "Nada acontece", "prioridade": prioridade,
             "solicitante_id": base["sol"]["id"], "ativo_id": base["ativo"]["id"], **extra}
    return cliente.post("/chamados", json=dados)


def test_abrir_calcula_sla_e_notifica(cliente, base):
    r = abrir(cliente, base, prioridade="critica")
    assert r.status_code == 201
    c = r.json()
    horas = (datetime.fromisoformat(c["prazo_sla"]) - datetime.fromisoformat(c["criado_em"])).total_seconds() / 3600
    assert round(horas) == 4
    avisos = cliente.get("/notificacoes", params={"destinatario_id": base["sol"]["id"]}).json()
    assert avisos[0]["tipo"] == "ChamadoAberto"


def test_abrir_com_solicitante_inexistente(cliente, base):
    assert abrir(cliente, base, solicitante_id=999).status_code == 404


def test_abrir_com_ativo_inexistente(cliente, base):
    assert abrir(cliente, base, ativo_id=999).status_code == 404


def test_atribuir_muda_status_e_avisa_tecnico(cliente, base):
    cid = abrir(cliente, base).json()["id"]
    r = cliente.patch(f"/chamados/{cid}/atribuir", json={"tecnico_id": base["tec"]["id"]})
    assert r.json()["status"] == "em_atendimento"
    avisos = cliente.get("/notificacoes", params={"destinatario_id": base["tec"]["id"]}).json()
    assert avisos[0]["tipo"] == "ChamadoAtribuido"


def test_so_tecnico_pode_ser_atribuido(cliente, base):
    cid = abrir(cliente, base).json()["id"]
    assert cliente.patch(f"/chamados/{cid}/atribuir", json={"tecnico_id": base["sol"]["id"]}).status_code == 422


def test_fluxo_completo_de_status(cliente, base):
    cid = abrir(cliente, base).json()["id"]
    cliente.patch(f"/chamados/{cid}/atribuir", json={"tecnico_id": base["tec"]["id"]})
    assert cliente.patch(f"/chamados/{cid}/status", json={"status": "resolvido"}).status_code == 200
    assert cliente.patch(f"/chamados/{cid}/status", json={"status": "fechado"}).json()["status"] == "fechado"


def test_transicao_invalida(cliente, base):
    cid = abrir(cliente, base).json()["id"]
    assert cliente.patch(f"/chamados/{cid}/status", json={"status": "fechado"}).status_code == 422


def test_iniciar_atendimento_sem_tecnico(cliente, base):
    cid = abrir(cliente, base).json()["id"]
    assert cliente.patch(f"/chamados/{cid}/status", json={"status": "em_atendimento"}).status_code == 422


def test_comentar(cliente, base):
    cid = abrir(cliente, base).json()["id"]
    r = cliente.post(f"/chamados/{cid}/comentarios", json={"autor_id": base["tec"]["id"], "texto": "Verificando a fonte."})
    assert r.status_code == 201
    assert len(cliente.get(f"/chamados/{cid}").json()["comentarios"]) == 1


def test_painel(cliente, base):
    abrir(cliente, base)
    abrir(cliente, base, prioridade="baixa")
    p = cliente.get("/chamados/painel").json()
    assert p["total"] == 2 and p["por_status"] == {"aberto": 2}
