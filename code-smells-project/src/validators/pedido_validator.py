from src.config.settings import STATUS_PEDIDO_VALIDOS
from src.errors import ValidationError


def _inteiro_positivo(valor):
    return isinstance(valor, int) and not isinstance(valor, bool) and valor > 0


def validar_pedido(dados):
    if not isinstance(dados, dict) or not dados:
        raise ValidationError("Dados inválidos")

    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens")
    if not usuario_id:
        raise ValidationError("Usuario ID é obrigatório")
    if not _inteiro_positivo(usuario_id):
        raise ValidationError("Usuario ID inválido")
    if not isinstance(itens, list) or not itens:
        raise ValidationError("Pedido deve ter pelo menos 1 item")
    for item in itens:
        if not isinstance(item, dict) or not _inteiro_positivo(item.get("produto_id")) \
                or not _inteiro_positivo(item.get("quantidade")):
            raise ValidationError("Cada item deve ter produto_id e quantidade inteiros e positivos")

    return {
        "usuario_id": usuario_id,
        "itens": [{"produto_id": item["produto_id"], "quantidade": item["quantidade"]} for item in itens],
    }


def validar_status(dados):
    status = dados.get("status") if isinstance(dados, dict) else None
    if status not in STATUS_PEDIDO_VALIDOS:
        raise ValidationError("Status inválido")
    return status
