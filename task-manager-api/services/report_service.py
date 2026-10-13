from datetime import timedelta

from sqlalchemy import case, func

from config.constants import (
    HIGH_PRIORITY_THRESHOLD,
    RECENT_ACTIVITY_DAYS,
    STATUS_CANCELLED,
    STATUS_DONE,
    STATUS_IN_PROGRESS,
    STATUS_PENDING,
)
from database import db
from middlewares.error_handler import NotFoundError
from models.category import Category
from models.task import Task
from models.user import User
from utils.datetime_utils import percentage, utcnow


def summary_report():
    now = utcnow()
    since = now - timedelta(days=RECENT_ACTIVITY_DAYS)
    overdue_tasks = Task.list_overdue(now)

    return {
        "generated_at": str(now),
        "overview": {
            "total_tasks": Task.count(),
            "total_users": db.session.scalar(db.select(func.count(User.id))),
            "total_categories": db.session.scalar(db.select(func.count(Category.id))),
        },
        "tasks_by_status": Task.count_by_status(),
        "tasks_by_priority": Task.count_by_priority(),
        "overdue": {
            "count": len(overdue_tasks),
            "tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "due_date": str(task.due_date),
                    "days_overdue": (now - task.due_date).days,
                }
                for task in overdue_tasks
            ],
        },
        "recent_activity": {
            "tasks_created_last_7_days": Task.count(Task.created_at >= since),
            "tasks_completed_last_7_days": Task.count(Task.status == STATUS_DONE, Task.updated_at >= since),
        },
        "user_productivity": _user_productivity(),
    }


def user_report(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        raise NotFoundError("Usuário não encontrado")

    now = utcnow()
    tasks = db.session.execute(db.select(Task).filter_by(user_id=user_id)).scalars().all()
    total = len(tasks)
    done = _count_status(tasks, STATUS_DONE)

    return {
        "user": {"id": user.id, "name": user.name, "email": user.email},
        "statistics": {
            "total_tasks": total,
            "done": done,
            "pending": _count_status(tasks, STATUS_PENDING),
            "in_progress": _count_status(tasks, STATUS_IN_PROGRESS),
            "cancelled": _count_status(tasks, STATUS_CANCELLED),
            "overdue": sum(1 for task in tasks if task.is_overdue(now)),
            "high_priority": sum(1 for task in tasks if task.priority <= HIGH_PRIORITY_THRESHOLD),
            "completion_rate": percentage(done, total),
        },
    }


def _user_productivity():
    done_count = func.coalesce(func.sum(case((Task.status == STATUS_DONE, 1), else_=0)), 0)
    stmt = (
        db.select(User.id, User.name, func.count(Task.id), done_count)
        .outerjoin(Task, Task.user_id == User.id)
        .group_by(User.id, User.name)
        .order_by(User.id)
    )
    return [
        {
            "user_id": user_id,
            "user_name": name,
            "total_tasks": total,
            "completed_tasks": completed,
            "completion_rate": percentage(completed, total),
        }
        for user_id, name, total, completed in db.session.execute(stmt).all()
    ]


def _count_status(tasks, status):
    return sum(1 for task in tasks if task.status == status)
