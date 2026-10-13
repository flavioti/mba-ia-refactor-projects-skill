from src.config.settings import FAIXAS_DESCONTO, STATUS_APROVADO, STATUS_CANCELADO, STATUS_PENDENTE


def calcular_desconto(faturamento):
    for minimo, taxa in FAIXAS_DESCONTO:
        if faturamento > minimo:
            return faturamento * taxa
    return 0


class RelatorioService:
    def __init__(self, pedido_model):
        self._pedidos = pedido_model

    def vendas(self):
        resumo = self._pedidos.resumo_por_status()
        total_pedidos = sum(grupo["quantidade"] for grupo in resumo.values())
        faturamento = sum(grupo["faturamento"] for grupo in resumo.values())
        desconto = calcular_desconto(faturamento)

        def quantidade(status):
            return resumo.get(status, {}).get("quantidade", 0)

        return {
            "total_pedidos": total_pedidos,
            "faturamento_bruto": round(faturamento, 2),
            "desconto_aplicavel": round(desconto, 2),
            "faturamento_liquido": round(faturamento - desconto, 2),
            "pedidos_pendentes": quantidade(STATUS_PENDENTE),
            "pedidos_aprovados": quantidade(STATUS_APROVADO),
            "pedidos_cancelados": quantidade(STATUS_CANCELADO),
            "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
        }
