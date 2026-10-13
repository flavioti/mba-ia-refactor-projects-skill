import logging

from sqlalchemy.orm import joinedload

from config.constants import STATUS_DONE
from database import db
from middlewares.error_handler import NotFoundError
from models.category import Category
from models.task import Task
from models.user import User
from utils.datetime_utils import percentage, utcnow
from validators.common import parse_int_param
from validators.task_validator import validate_task_payload

logger = logging.getLogger(__name__)


def list_tasks():
    stmt = db.select(Task).options(joinedload(Task.user), joinedload(Task.category))
    tasks = db.session.execute(stmt).scalars().all()
    return [task.to_dict(include_relations=True) for task in tasks]


def get_task(task_id):
    return _get_task_or_404(task_id).to_dict()


def create_task(payload):
    data = validate_task_payload(payload)
    _ensure_references_exist(data)
    task = Task(**data)
    db.session.add(task)
    db.session.commit()
    logger.info("Task criada: id=%s", task.id)
    return task.to_dict()


def update_task(task_id, payload):
    task = _get_task_or_404(task_id)
    data = validate_task_payload(payload, partial=True)
    _ensure_references_exist(data)
    for field, value in data.items():
        setattr(task, field, value)
    task.updated_at = utcnow()
    db.session.commit()
    logger.info("Task atualizada: id=%s", task.id)
    return task.to_dict()


def delete_task(task_id):
    task = _get_task_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    logger.info("Task deletada: id=%s", task_id)


def search_tasks(args):
    stmt = db.select(Task)
    query = args.get("q", "")
    if query:
        stmt = stmt.where(db.or_(Task.title.like(f"%{query}%"), Task.description.like(f"%{query}%")))
    status = args.get("status", "")
    if status:
        stmt = stmt.where(Task.status == status)
    priority = parse_int_param(args.get("priority"), "priority")
    if priority is not None:
        stmt = stmt.where(Task.priority == priority)
    user_id = parse_int_param(args.get("user_id"), "user_id")
    if user_id is not None:
        stmt = stmt.where(Task.user_id == user_id)
    return [task.to_dict() for task in db.session.execute(stmt).scalars().all()]


def task_stats():
    by_status = Task.count_by_status()
    total = sum(by_status.values())
    return {
        "total": total,
        **by_status,
        "overdue": Task.count(*Task.overdue_filter(utcnow())),
        "completion_rate": percentage(by_status[STATUS_DONE], total),
    }


def _get_task_or_404(task_id):
    task = db.session.get(Task, task_id)
    if task is None:
        raise NotFoundError("Task não encontrada")
    return task


def _ensure_references_exist(data):
    if data.get("user_id") and db.session.get(User, data["user_id"]) is None:
        raise NotFoundError("Usuário não encontrado")
    if data.get("category_id") and db.session.get(Category, data["category_id"]) is None:
        raise NotFoundError("Categoria não encontrada")
