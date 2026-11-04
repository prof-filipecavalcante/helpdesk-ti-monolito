"""Erros de negócio compartilhados pelos módulos."""


class NaoEncontrado(Exception):
    """O recurso pedido não existe."""


class RegraDeNegocio(Exception):
    """A operação viola uma regra do sistema."""
