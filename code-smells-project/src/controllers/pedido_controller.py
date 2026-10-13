from src.validators.pedido_validator import validar_pedido, validar_status


class PedidoController:
    def __init__(self, pedido_service, pedido_model):
        self._service = pedido_service
        self._pedidos = pedido_model

    def criar(self, dados):
        pedido = validar_pedido(dados)
        return self._service.criar(pedido["usuario_id"], pedido["itens"])

    def listar(self, usuario_id=None):
        return self._pedidos.listar(usuario_id)

    def atualizar_status(self, pedido_id, dados):
        self._service.atualizar_status(pedido_id, validar_status(dados))
