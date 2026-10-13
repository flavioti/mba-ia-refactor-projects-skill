from src.config.settings import STATUS_PENDENTE
from src.errors import ValidationError

PRODUTO_REMOVIDO = "Desconhecido"


class PedidoModel:
    def __init__(self, get_db):
        self._get_db = get_db

    def listar(self, usuario_id=None):
        rows = self._get_db().execute(
            """
            SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,
                   i.produto_id, i.quantidade, i.preco_unitario,
                   COALESCE(pr.nome, :removido) AS produto_nome
            FROM pedidos p
            LEFT JOIN itens_pedido i ON i.pedido_id = p.id
            LEFT JOIN produtos pr ON pr.id = i.produto_id
            WHERE (:usuario_id IS NULL OR p.usuario_id = :usuario_id)
            ORDER BY p.id, i.id
            """,
            {"usuario_id": usuario_id, "removido": PRODUTO_REMOVIDO},
        ).fetchall()

        pedidos = {}
        for row in rows:
            pedido = pedidos.setdefault(row["id"], {
                "id": row["id"],
                "usuario_id": row["usuario_id"],
                "status": row["status"],
                "total": row["total"],
                "criado_em": row["criado_em"],
                "itens": [],
            })
            if row["produto_id"] is not None:
                pedido["itens"].append({
                    "produto_id": row["produto_id"],
                    "produto_nome": row["produto_nome"],
                    "quantidade": row["quantidade"],
                    "preco_unitario": row["preco_unitario"],
                })
        return list(pedidos.values())

    def criar(self, usuario_id, total, itens):
        """Grava pedido, itens e baixa de estoque numa única transação.

        `itens`: lista de dicts com produto_id, quantidade, preco_unitario e produto_nome.
        """
        conn = self._get_db()
        with conn:
            cursor = conn.execute(
                "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
                (usuario_id, STATUS_PENDENTE, total),
            )
            pedido_id = cursor.lastrowid
            for item in itens:
                conn.execute(
                    "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
                    (pedido_id, item["produto_id"], item["quantidade"], item["preco_unitario"]),
                )
                baixa = conn.execute(
                    "UPDATE produtos SET estoque = estoque - ? WHERE id = ? AND estoque >= ?",
                    (item["quantidade"], item["produto_id"], item["quantidade"]),
                )
                if baixa.rowcount == 0:
                    # exceção dentro do `with` desfaz toda a transação
                    raise ValidationError("Estoque insuficiente para " + item["produto_nome"])
        return pedido_id

    def atualizar_status(self, pedido_id, status):
        conn = self._get_db()
        with conn:
            conn.execute("UPDATE pedidos SET status = ? WHERE id = ?", (status, pedido_id))

    def resumo_por_status(self):
        rows = self._get_db().execute(
            "SELECT status, COUNT(*) AS quantidade, COALESCE(SUM(total), 0) AS faturamento FROM pedidos GROUP BY status"
        ).fetchall()
        return {row["status"]: {"quantidade": row["quantidade"], "faturamento": row["faturamento"]} for row in rows}

    def contar(self):
        return self._get_db().execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
