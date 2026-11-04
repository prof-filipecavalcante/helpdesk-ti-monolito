"""Cria dados de exemplo quando o banco está vazio."""
from sqlalchemy.orm import Session

from app.chamados import servico as chamados
from app.chamados.esquemas import ChamadoCriar
from app.inventario import servico as inventario
from app.inventario.esquemas import AtivoCriar
from app.usuarios import servico as usuarios
from app.usuarios.esquemas import UsuarioCriar


def carregar(db: Session) -> None:
    if usuarios.listar(db):
        return
    ana = usuarios.criar(db, UsuarioCriar(nome="Ana Souza", email="ana@empresa.com", perfil="solicitante"))
    bruno = usuarios.criar(db, UsuarioCriar(nome="Bruno Lima", email="bruno@empresa.com", perfil="solicitante"))
    carla = usuarios.criar(db, UsuarioCriar(nome="Carla Dias", email="carla@empresa.com", perfil="tecnico"))
    usuarios.criar(db, UsuarioCriar(nome="Diego Rocha", email="diego@empresa.com", perfil="tecnico"))

    pc = inventario.criar(db, AtivoCriar(patrimonio="PAT-0001", tipo="computador", descricao="Desktop Dell OptiPlex", setor="Financeiro"))
    imp = inventario.criar(db, AtivoCriar(patrimonio="PAT-0002", tipo="impressora", descricao="Impressora HP LaserJet", setor="RH"))
    inventario.criar(db, AtivoCriar(patrimonio="PAT-0003", tipo="notebook", descricao="Notebook Lenovo ThinkPad", setor="TI"))

    c1 = chamados.abrir(db, ChamadoCriar(titulo="Computador não liga", descricao="Apertei o botão e nada acontece.", prioridade="alta", solicitante_id=ana.id, ativo_id=pc.id))
    chamados.abrir(db, ChamadoCriar(titulo="Impressora atolando papel", descricao="Atola a cada 3 folhas.", prioridade="media", solicitante_id=bruno.id, ativo_id=imp.id))
    chamados.abrir(db, ChamadoCriar(titulo="Acesso ao sistema de RH", descricao="Preciso de acesso para a nova estagiária.", prioridade="baixa", solicitante_id=bruno.id))
    chamados.atribuir(db, c1.id, carla.id)
