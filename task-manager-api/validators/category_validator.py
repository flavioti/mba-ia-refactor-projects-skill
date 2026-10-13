import re

from config.constants import COLOR_PATTERN, DEFAULT_COLOR
from middlewares.error_handler import ValidationError
from validators.common import require_json_object


def validate_category_create(data):
    require_json_object(data)
    if not data.get("name"):
        raise ValidationError("Nome é obrigatório")
    return {
        "name": data["name"],
        "description": data.get("description", ""),
        "color": _validate_color(data.get("color", DEFAULT_COLOR)),
    }


def validate_category_update(data):
    require_json_object(data, allow_empty=True)
    cleaned = {}
    if "name" in data:
        if not data["name"]:
            raise ValidationError("Nome é obrigatório")
        cleaned["name"] = data["name"]
    if "description" in data:
        cleaned["description"] = data["description"]
    if "color" in data:
        cleaned["color"] = _validate_color(data["color"])
    return cleaned


def _validate_color(color):
    if not isinstance(color, str) or not re.match(COLOR_PATTERN, color):
        raise ValidationError("Cor inválida. Use o formato #RRGGBB")
    return color
