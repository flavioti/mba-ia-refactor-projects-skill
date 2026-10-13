import re

from config.constants import EMAIL_PATTERN, MIN_PASSWORD_LENGTH, ROLE_USER, VALID_ROLES
from middlewares.error_handler import ValidationError
from validators.common import require_json_object


def validate_user_create(data):
    require_json_object(data)
    name, email, password = data.get("name"), data.get("email"), data.get("password")
    if not name:
        raise ValidationError("Nome é obrigatório")
    if not email:
        raise ValidationError("Email é obrigatório")
    if not password:
        raise ValidationError("Senha é obrigatória")
    _validate_email(email)
    if not isinstance(password, str) or len(password) < MIN_PASSWORD_LENGTH:
        raise ValidationError(f"Senha deve ter no mínimo {MIN_PASSWORD_LENGTH} caracteres")
    role = data.get("role", ROLE_USER)
    _validate_role(role)
    return {"name": name, "email": email, "password": password, "role": role}


def validate_user_update(data):
    require_json_object(data)
    cleaned = {}
    if "name" in data:
        if not isinstance(data["name"], str) or not data["name"].strip():
            raise ValidationError("Nome é obrigatório")
        cleaned["name"] = data["name"]
    if "email" in data:
        cleaned["email"] = _validate_email(data["email"])
    if "password" in data:
        if not isinstance(data["password"], str) or len(data["password"]) < MIN_PASSWORD_LENGTH:
            raise ValidationError("Senha muito curta")
        cleaned["password"] = data["password"]
    if "role" in data:
        cleaned["role"] = _validate_role(data["role"])
    if "active" in data:
        if not isinstance(data["active"], bool):
            raise ValidationError("Campo active deve ser booleano")
        cleaned["active"] = data["active"]
    return cleaned


def validate_login(data):
    require_json_object(data)
    email, password = data.get("email"), data.get("password")
    if not email or not password:
        raise ValidationError("Email e senha são obrigatórios")
    return email, password


def _validate_email(email):
    if not isinstance(email, str) or not re.match(EMAIL_PATTERN, email):
        raise ValidationError("Email inválido")
    return email


def _validate_role(role):
    if role not in VALID_ROLES:
        raise ValidationError("Role inválido")
    return role
