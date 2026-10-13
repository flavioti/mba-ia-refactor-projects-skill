from functools import wraps

from flask import current_app, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from src.errors import ForbiddenError, UnauthorizedError


def _serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="auth")


def issue_token(usuario):
    return _serializer().dumps({"id": usuario["id"], "tipo": usuario["tipo"]})


def require_auth(tipo=None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            header = request.headers.get("Authorization", "")
            if not header.startswith("Bearer "):
                raise UnauthorizedError("Token ausente")
            try:
                payload = _serializer().loads(header[len("Bearer "):], max_age=current_app.config["TOKEN_MAX_AGE"])
            except (BadSignature, SignatureExpired):
                raise UnauthorizedError("Token inválido") from None
            if tipo and payload.get("tipo") != tipo:
                raise ForbiddenError("Acesso negado")
            return fn(*args, **kwargs)
        return wrapper
    return decorator
