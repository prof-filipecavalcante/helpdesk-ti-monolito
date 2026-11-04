def test_cria_e_lista_usuarios(cliente):
    r = cliente.post("/usuarios", json={"nome": "Ana", "email": "ana@x.com", "perfil": "solicitante"})
    assert r.status_code == 201
    assert cliente.get("/usuarios").json()[0]["nome"] == "Ana"


def test_email_repetido_e_recusado(cliente):
    dados = {"nome": "Ana", "email": "ana@x.com", "perfil": "solicitante"}
    cliente.post("/usuarios", json=dados)
    assert cliente.post("/usuarios", json=dados).status_code == 422


def test_usuario_inexistente(cliente):
    assert cliente.get("/usuarios/99").status_code == 404


def test_cria_ativo_e_filtra_por_setor(cliente):
    cliente.post("/ativos", json={"patrimonio": "PAT-1", "tipo": "impressora", "descricao": "HP", "setor": "RH"})
    cliente.post("/ativos", json={"patrimonio": "PAT-2", "tipo": "computador", "descricao": "Dell", "setor": "TI"})
    assert len(cliente.get("/ativos", params={"setor": "RH"}).json()) == 1
