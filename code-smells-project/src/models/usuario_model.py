from werkzeug.security import check_password_hash, generate_password_hash

from src.config.settings import TIPO_CLIENTE

CAMPOS_PUBLICOS = ("id", "nome", "email", "tipo", "criado_em")
COLUNAS_PUBLICAS = ", ".join(CAMPOS_PUBLICOS)


def usuario_to_dict(row):
    """Serialização pública: nunca inclui a senha."""
    return {campo: row[campo] for campo in CAMPOS_PUBLICOS}


class UsuarioModel:
    def __init__(self, get_db):
        self._get_db = get_db

    def listar(self):
        rows = self._get_db().execute(f"SELECT {COLUNAS_PUBLICAS} FROM usuarios").fetchall()
        return [usuario_to_dict(row) for row in rows]

    def buscar_por_id(self, usuario_id):
        row = self._get_db().execute(
            f"SELECT {COLUNAS_PUBLICAS} FROM usuarios WHERE id = ?", (usuario_id,)
        ).fetchone()
        return usuario_to_dict(row) if row else None

    def criar(self, nome, email, senha, tipo=TIPO_CLIENTE):
        conn = self._get_db()
        with conn:
            cursor = conn.execute(
                "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
                (nome, email, generate_password_hash(senha), tipo),
            )
        return cursor.lastrowid

    def autenticar(self, email, senha):
        """Retorna o usuário (sem senha) se as credenciais conferem, senão None."""
        rows = self._get_db().execute(
            "SELECT id, nome, email, tipo, senha FROM usuarios WHERE email = ? ORDER BY id", (email,)
        ).fetchall()
        for row in rows:
            if row["senha"] and check_password_hash(row["senha"], senha):
                return {"id": row["id"], "nome": row["nome"], "email": row["email"], "tipo": row["tipo"]}
        return None

    def contar(self):
        return self._get_db().execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
