from datetime import datetime

from config.constants import (
    DATE_FORMAT,
    DEFAULT_PRIORITY,
    MAX_PRIORITY,
    MAX_TITLE_LENGTH,
    MIN_PRIORITY,
    MIN_TITLE_LENGTH,
    STATUS_PENDING,
    VALID_STATUSES,
)
from middlewares.error_handler import ValidationError
from validators.common import is_int, require_json_object


def validate_task_payload(data, partial=False):
    """Valida o payload de criação (partial=False) ou atualização (partial=True) de task.

    Retorna apenas os campos presentes, já normalizados para o model.
    """
    require_json_object(data)
    if not partial:
        if not data.get("title"):
            raise ValidationError("Título é obrigatório")
        data = {"description": "", "status": STATUS_PENDING, "priority": DEFAULT_PRIORITY, **data}

    cleaned = {}
    if "title" in data:
        cleaned["title"] = _validate_title(data["title"])
    if "description" in data:
        cleaned["description"] = data["description"]
    if "status" in data:
        cleaned["status"] = _validate_status(data["status"])
    if "priority" in data:
        cleaned["priority"] = _validate_priority(data["priority"])
    for field in ("user_id", "category_id"):
        if field in data:
            cleaned[field] = _validate_reference(data[field], field)
    if "due_date" in data:
        cleaned["due_date"] = _parse_due_date(data["due_date"])
    if "tags" in data:
        cleaned["tags"] = _normalize_tags(data["tags"])
    return cleaned


def _validate_title(title):
    if not isinstance(title, str) or not title:
        raise ValidationError("Título é obrigatório")
    if len(title) < MIN_TITLE_LENGTH:
        raise ValidationError("Título muito curto")
    if len(title) > MAX_TITLE_LENGTH:
        raise ValidationError("Título muito longo")
    return title


def _validate_status(status):
    if status not in VALID_STATUSES:
        raise ValidationError("Status inválido")
    return status


def _validate_priority(priority):
    if not is_int(priority) or not MIN_PRIORITY <= priority <= MAX_PRIORITY:
        raise ValidationError(f"Prioridade deve ser entre {MIN_PRIORITY} e {MAX_PRIORITY}")
    return priority


def _validate_reference(value, field):
    if not value:
        return None
    if not is_int(value):
        raise ValidationError(f"{field} inválido")
    return value


def _parse_due_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, DATE_FORMAT)
    except (TypeError, ValueError):
        raise ValidationError("Formato de data inválido. Use YYYY-MM-DD")


def _normalize_tags(tags):
    if tags is None or isinstance(tags, str):
        return tags
    if isinstance(tags, list) and all(isinstance(tag, str) for tag in tags):
        return ",".join(tags)
    raise ValidationError("Tags devem ser uma lista de textos")
