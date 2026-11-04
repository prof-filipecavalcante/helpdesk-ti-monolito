"""Cria dados de exemplo quando o banco está vazio.

Uso apenas em aula: todos os usuários de exemplo têm a mesma senha
(variável SENHA_EXEMPLO). Em produção, rode com DADOS_EXEMPLO=0.
"""
import os

from sqlalchemy.orm import Session

from app.chamados import servico as chamados
from app.chamados.esquemas import ChamadoCriar
from app.inventario import servico as inventario
from app.inventario.esquemas import AtivoCriar
from app.usuarios import servico as usuarios
from app.usuarios.esquemas import UsuarioCriar

SENHA = os.getenv("SENHA_EXEMPLO", "Helpdesk2026")


def carregar(db: Session) -> None:
    if usuarios.listar(db):
        return
    novo = lambda nome, email, perfil: usuarios.criar(db, UsuarioCriar(nome=nome, email=email, perfil=perfil, senha=SENHA))
    novo("Admin TI", "admin@empresa.com", "admin")
    ana = novo("Ana Souza", "ana@empresa.com", "solicitante")
    bruno = novo("Bruno Lima", "bruno@empresa.com", "solicitante")
    carla = novo("Carla Dias", "carla@empresa.com", "tecnico")
    novo("Diego Rocha", "diego@empresa.com", "tecnico")

    pc = inventario.criar(db, AtivoCriar(patrimonio="PAT-0001", tipo="computador", descricao="Desktop Dell OptiPlex", setor="Financeiro"))
    imp = inventario.criar(db, AtivoCriar(patrimonio="PAT-0002", tipo="impressora", descricao="Impressora HP LaserJet", setor="RH"))
    inventario.criar(db, AtivoCriar(patrimonio="PAT-0003", tipo="notebook", descricao="Notebook Lenovo ThinkPad", setor="TI"))

    c1 = chamados.abrir(db, ChamadoCriar(titulo="Computador não liga", descricao="Apertei o botão e nada acontece.", prioridade="alta", ativo_id=pc.id), ana)
    chamados.abrir(db, ChamadoCriar(titulo="Impressora atolando papel", descricao="Atola a cada 3 folhas.", prioridade="media", ativo_id=imp.id), bruno)
    chamados.abrir(db, ChamadoCriar(titulo="Acesso ao sistema de RH", descricao="Preciso de acesso para a nova estagiária.", prioridade="baixa"), bruno)
    chamados.atribuir(db, c1.id, carla.id, carla)
