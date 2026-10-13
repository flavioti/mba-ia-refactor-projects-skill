from functools import wraps

from flask import current_app, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from database import db
from middlewares.error_handler import ForbiddenError, UnauthorizedError
from models.user import User

_TOKEN_SALT = "auth-token"
_BEARER_PREFIX = "Bearer "


def _serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt=_TOKEN_SALT)


def issue_token(user):
    return _serializer().dumps({"id": user.id})


def get_current_user():
    """Usuário autenticado pelo header Authorization, ou None se não houver token."""
    header = request.headers.get("Authorization", "")
    if not header.startswith(_BEARER_PREFIX):
        return None
    try:
        payload = _serializer().loads(
            header[len(_BEARER_PREFIX):],
            max_age=current_app.config["TOKEN_MAX_AGE_SECONDS"],
        )
    except (BadSignature, SignatureExpired):
        raise UnauthorizedError("Token inválido ou expirado")

    user = db.session.get(User, payload.get("id"))
    if user is None or not user.active:
        raise UnauthorizedError("Token inválido ou expirado")
    return user


def is_admin_request():
    user = get_current_user()
    return user is not None and user.is_admin()


def require_admin(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if user is None:
            raise UnauthorizedError("Autenticação necessária")
        if not user.is_admin():
            raise ForbiddenError("Acesso restrito a administradores")
        return view(*args, **kwargs)

    return wrapper
