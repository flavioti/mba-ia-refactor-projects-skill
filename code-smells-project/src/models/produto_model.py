CAMPOS = ("id", "nome", "descricao", "preco", "estoque", "categoria", "ativo", "criado_em")
COLUNAS = ", ".join(CAMPOS)


def produto_to_dict(row):
    return {campo: row[campo] for campo in CAMPOS}


class ProdutoModel:
    def __init__(self, get_db):
        self._get_db = get_db

    def listar(self):
        rows = self._get_db().execute(f"SELECT {COLUNAS} FROM produtos").fetchall()
        return [produto_to_dict(row) for row in rows]

    def buscar_por_id(self, produto_id):
        row = self._get_db().execute(f"SELECT {COLUNAS} FROM produtos WHERE id = ?", (produto_id,)).fetchone()
        return produto_to_dict(row) if row else None

    def buscar_por_ids(self, produto_ids):
        ids = list(produto_ids)
        if not ids:
            return {}
        placeholders = ", ".join("?" for _ in ids)
        rows = self._get_db().execute(f"SELECT {COLUNAS} FROM produtos WHERE id IN ({placeholders})", ids).fetchall()
        return {row["id"]: produto_to_dict(row) for row in rows}

    def buscar(self, termo=None, categoria=None, preco_min=None, preco_max=None):
        clauses, params = [], []
        if termo:
            clauses.append("(nome LIKE ? OR descricao LIKE ?)")
            params += [f"%{termo}%", f"%{termo}%"]
        if categoria:
            clauses.append("categoria = ?")
            params.append(categoria)
        if preco_min is not None:
            clauses.append("preco >= ?")
            params.append(preco_min)
        if preco_max is not None:
            clauses.append("preco <= ?")
            params.append(preco_max)
        where = " AND ".join(clauses) or "1=1"
        rows = self._get_db().execute(f"SELECT {COLUNAS} FROM produtos WHERE {where}", params).fetchall()
        return [produto_to_dict(row) for row in rows]

    def criar(self, dados):
        conn = self._get_db()
        with conn:
            cursor = conn.execute(
                "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
                (dados["nome"], dados["descricao"], dados["preco"], dados["estoque"], dados["categoria"]),
            )
        return cursor.lastrowid

    def atualizar(self, produto_id, dados):
        conn = self._get_db()
        with conn:
            conn.execute(
                "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
                (dados["nome"], dados["descricao"], dados["preco"], dados["estoque"], dados["categoria"], produto_id),
            )

    def deletar(self, produto_id):
        # itens_pedido é histórico (guarda preco_unitario); a leitura de pedidos trata produto removido.
        conn = self._get_db()
        with conn:
            conn.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))

    def contar(self):
        return self._get_db().execute("SELECT COUNT(*) FROM produtos").fetchone()[0]
