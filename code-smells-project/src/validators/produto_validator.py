from src.config.settings import CATEGORIA_PADRAO, CATEGORIAS_VALIDAS, NOME_PRODUTO_MAX, NOME_PRODUTO_MIN
from src.errors import ValidationError

CAMPOS_OBRIGATORIOS = (("nome", "Nome"), ("preco", "Preço"), ("estoque", "Estoque"))


def _is_number(valor):
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def validar_produto(dados):
    """Valida o payload de criação/atualização de produto e retorna os campos normalizados."""
    if not isinstance(dados, dict) or not dados:
        raise ValidationError("Dados inválidos")
    for campo, rotulo in CAMPOS_OBRIGATORIOS:
        if campo not in dados:
            raise ValidationError(f"{rotulo} é obrigatório")

    nome = dados["nome"]
    descricao = dados.get("descricao", "")
    preco = dados["preco"]
    estoque = dados["estoque"]
    categoria = dados.get("categoria", CATEGORIA_PADRAO)

    if not isinstance(nome, str):
        raise ValidationError("Nome inválido")
    if not isinstance(descricao, str):
        raise ValidationError("Descrição inválida")
    if not _is_number(preco):
        raise ValidationError("Preço inválido")
    if not isinstance(estoque, int) or isinstance(estoque, bool):
        raise ValidationError("Estoque inválido")
    if preco < 0:
        raise ValidationError("Preço não pode ser negativo")
    if estoque < 0:
        raise ValidationError("Estoque não pode ser negativo")
    if len(nome) < NOME_PRODUTO_MIN:
        raise ValidationError("Nome muito curto")
    if len(nome) > NOME_PRODUTO_MAX:
        raise ValidationError("Nome muito longo")
    if categoria not in CATEGORIAS_VALIDAS:
        raise ValidationError("Categoria inválida. Válidas: " + str(list(CATEGORIAS_VALIDAS)))

    return {"nome": nome, "descricao": descricao, "preco": preco, "estoque": estoque, "categoria": categoria}


def parse_preco(valor, parametro):
    """Converte parâmetro de query string opcional em float."""
    if not valor:
        return None
    try:
        return float(valor)
    except ValueError:
        raise ValidationError(f"Parâmetro {parametro} inválido") from None
