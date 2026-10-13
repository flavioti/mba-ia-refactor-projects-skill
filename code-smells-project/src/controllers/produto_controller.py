import logging

from src.errors import NotFoundError
from src.validators.produto_validator import parse_preco, validar_produto

logger = logging.getLogger(__name__)


class ProdutoController:
    def __init__(self, produto_model):
        self._produtos = produto_model

    def listar(self):
        produtos = self._produtos.listar()
        logger.debug("Listando %s produtos", len(produtos))
        return produtos

    def obter(self, produto_id):
        produto = self._produtos.buscar_por_id(produto_id)
        if produto is None:
            raise NotFoundError("Produto não encontrado")
        return produto

    def buscar(self, termo, categoria, preco_min, preco_max):
        return self._produtos.buscar(
            termo=termo,
            categoria=categoria,
            preco_min=parse_preco(preco_min, "preco_min"),
            preco_max=parse_preco(preco_max, "preco_max"),
        )

    def criar(self, dados):
        produto_id = self._produtos.criar(validar_produto(dados))
        logger.info("Produto criado com ID %s", produto_id)
        return produto_id

    def atualizar(self, produto_id, dados):
        self.obter(produto_id)
        self._produtos.atualizar(produto_id, validar_produto(dados))

    def deletar(self, produto_id):
        self.obter(produto_id)
        self._produtos.deletar(produto_id)
        logger.info("Produto %s deletado", produto_id)
