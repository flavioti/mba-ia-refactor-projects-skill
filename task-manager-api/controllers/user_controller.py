import logging

from config.constants import ROLE_USER
from database import db
from middlewares.auth import is_admin_request, issue_token
from middlewares.error_handler import ConflictError, ForbiddenError, NotFoundError, UnauthorizedError
from models.task import Task
from models.user import User
from validators.user_validator import validate_login, validate_user_create, validate_user_update

logger = logging.getLogger(__name__)


def list_users():
    users = db.session.execute(db.select(User).order_by(User.id)).scalars().all()
    task_counts = Task.count_by(Task.user_id)
    return [{**user.to_dict(), "task_count": task_counts.get(user.id, 0)} for user in users]


def get_user(user_id):
    user = _get_user_or_404(user_id)
    return {**user.to_dict(), "tasks": [task.to_dict() for task in _tasks_of(user_id)]}


def create_user(payload):
    data = validate_user_create(payload)
    if User.find_by_email(data["email"]):
        raise ConflictError("Email já cadastrado")
    if data["role"] != ROLE_USER and not is_admin_request():
        raise ForbiddenError("Apenas administradores podem definir o role")

    user = User(name=data["name"], email=data["email"], role=data["role"])
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
    logger.info("Usuário criado: id=%s", user.id)
    return user.to_dict()


def update_user(user_id, payload):
    user = _get_user_or_404(user_id)
    data = validate_user_update(payload)

    if "email" in data:
        existing = User.find_by_email(data["email"])
        if existing and existing.id != user_id:
            raise ConflictError("Email já cadastrado")
    if "role" in data and data["role"] != user.role and not is_admin_request():
        raise ForbiddenError("Apenas administradores podem alterar o role")

    password = data.pop("password", None)
    if password:
        user.set_password(password)
    for field, value in data.items():
        setattr(user, field, value)
    db.session.commit()
    return user.to_dict()


def delete_user(user_id):
    user = _get_user_or_404(user_id)
    for task in _tasks_of(user_id):
        db.session.delete(task)
    db.session.delete(user)
    db.session.commit()
    logger.info("Usuário deletado: id=%s", user_id)


def get_user_tasks(user_id):
    _get_user_or_404(user_id)
    return [task.to_dict() for task in _tasks_of(user_id)]


def login(payload):
    email, password = validate_login(payload)
    user = User.find_by_email(email)
    if user is None or not user.check_password(password):
        raise UnauthorizedError("Credenciais inválidas")
    if not user.active:
        raise ForbiddenError("Usuário inativo")
    return {
        "message": "Login realizado com sucesso",
        "user": user.to_dict(),
        "token": issue_token(user),
    }


def _get_user_or_404(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        raise NotFoundError("Usuário não encontrado")
    return user


def _tasks_of(user_id):
    return db.session.execute(db.select(Task).filter_by(user_id=user_id).order_by(Task.id)).scalars().all()
