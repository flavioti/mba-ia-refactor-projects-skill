import os
import secrets


def _bool(value, default=False):
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


class Settings:
    # Sem SECRET_KEY no ambiente, gera uma chave efêmera (tokens expiram a cada restart).
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    DEBUG = _bool(os.environ.get("FLASK_DEBUG"))
    HOST = os.environ.get("HOST", "127.0.0.1")
    PORT = int(os.environ.get("PORT", "5000"))
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "loja.db")
    APP_ENV = os.environ.get("APP_ENV", "development")
    TOKEN_MAX_AGE = int(os.environ.get("TOKEN_MAX_AGE", "3600"))


API_VERSION = "1.0.0"

# Produtos
CATEGORIAS_VALIDAS = ("informatica", "moveis", "vestuario", "geral", "eletronicos", "livros")
CATEGORIA_PADRAO = "geral"
NOME_PRODUTO_MIN = 2
NOME_PRODUTO_MAX = 200

# Usuários
TIPO_CLIENTE = "cliente"
TIPO_ADMIN = "admin"

# Pedidos
STATUS_PENDENTE = "pendente"
STATUS_APROVADO = "aprovado"
STATUS_ENVIADO = "enviado"
STATUS_ENTREGUE = "entregue"
STATUS_CANCELADO = "cancelado"
STATUS_PEDIDO_VALIDOS = (STATUS_PENDENTE, STATUS_APROVADO, STATUS_ENVIADO, STATUS_ENTREGUE, STATUS_CANCELADO)

# Relatório de vendas: (faturamento mínimo exclusivo, taxa de desconto), da maior faixa para a menor
FAIXAS_DESCONTO = ((10000, 0.10), (5000, 0.05), (1000, 0.02))
