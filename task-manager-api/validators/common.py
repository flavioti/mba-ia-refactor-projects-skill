from middlewares.error_handler import ValidationError


def require_json_object(data, allow_empty=False):
    if not isinstance(data, dict) or (not data and not allow_empty):
        raise ValidationError("Dados inválidos")
    return data


def parse_int_param(value, name):
    """Converte parâmetro de query string em int; vazio vira None."""
    if value in (None, ""):
        return None
    try:
        return int(value)
    except ValueError:
        raise ValidationError(f"Parâmetro {name} inválido")


def is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)
