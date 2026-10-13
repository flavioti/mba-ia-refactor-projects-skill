from src.errors import ValidationError


class PedidoService:
    def __init__(self, produto_model, pedido_model, notificador):
        self._produtos = produto_model
        self._pedidos = pedido_model
        self._notificador = notificador

    def criar(self, usuario_id, itens):
        produtos = self._produtos.buscar_por_ids({item["produto_id"] for item in itens})

        # valida tudo antes de qualquer escrita
        total = 0
        itens_pedido = []
        for item in itens:
            produto = produtos.get(item["produto_id"])
            if produto is None:
                raise ValidationError("Produto " + str(item["produto_id"]) + " não encontrado")
            if produto["estoque"] < item["quantidade"]:
                raise ValidationError("Estoque insuficiente para " + produto["nome"])
            total += produto["preco"] * item["quantidade"]
            itens_pedido.append({
                "produto_id": produto["id"],
                "produto_nome": produto["nome"],
                "quantidade": item["quantidade"],
                "preco_unitario": produto["preco"],
            })

        pedido_id = self._pedidos.criar(usuario_id, total, itens_pedido)
        self._notificador.pedido_criado(pedido_id, usuario_id)
        return {"pedido_id": pedido_id, "total": total}

    def atualizar_status(self, pedido_id, status):
        self._pedidos.atualizar_status(pedido_id, status)
        self._notificador.status_alterado(pedido_id, status)
