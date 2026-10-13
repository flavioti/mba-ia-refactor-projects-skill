import logging

from src.config.settings import API_VERSION

logger = logging.getLogger(__name__)


class SistemaController:
    """Endpoints de infraestrutura: índice, health check, relatório e administração."""

    def __init__(self, produto_model, usuario_model, pedido_model, relatorio_service, resetar_dados, ambiente):
        self._produtos = produto_model
        self._usuarios = usuario_model
        self._pedidos = pedido_model
        self._relatorio = relatorio_service
        self._resetar_dados = resetar_dados
        self._ambiente = ambiente

    def indice(self):
        return {
            "mensagem": "Bem-vindo à API da Loja",
            "versao": API_VERSION,
            "endpoints": {
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health",
            },
        }

    def health(self):
        return {
            "status": "ok",
            "database": "connected",
            "counts": {
                "produtos": self._produtos.contar(),
                "usuarios": self._usuarios.contar(),
                "pedidos": self._pedidos.contar(),
            },
            "versao": API_VERSION,
            "ambiente": self._ambiente,
        }

    def relatorio_vendas(self):
        return self._relatorio.vendas()

    def resetar_banco(self):
        self._resetar_dados()
        logger.warning("Banco de dados resetado por um administrador")
