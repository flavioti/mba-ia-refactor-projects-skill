from sqlalchemy import func

from config.constants import CLOSED_STATUSES, DEFAULT_PRIORITY, PRIORITY_LABELS, STATUS_PENDING, VALID_STATUSES
from database import db
from utils.datetime_utils import utcnow


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default=STATUS_PENDING)
    priority = db.Column(db.Integer, default=DEFAULT_PRIORITY)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    tags = db.Column(db.String(500), nullable=True)

    user = db.relationship("User", backref="tasks")
    category = db.relationship("Category", backref="tasks")

    def is_overdue(self, now=None):
        now = now or utcnow()
        return self.due_date is not None and self.due_date < now and self.status not in CLOSED_STATUSES

    def to_dict(self, include_relations=False):
        data = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
            "due_date": str(self.due_date) if self.due_date else None,
            "tags": self.tags.split(",") if self.tags else [],
            "overdue": self.is_overdue(),
        }
        if include_relations:
            data["user_name"] = self.user.name if self.user else None
            data["category_name"] = self.category.name if self.category else None
        return data

    # --- Consultas agregadas (evitam N+1 e contagens repetidas) ---

    @classmethod
    def overdue_filter(cls, now):
        return (cls.due_date.is_not(None), cls.due_date < now, cls.status.not_in(CLOSED_STATUSES))

    @classmethod
    def list_overdue(cls, now):
        return db.session.execute(db.select(cls).where(*cls.overdue_filter(now)).order_by(cls.id)).scalars().all()

    @classmethod
    def count(cls, *conditions):
        return db.session.scalar(db.select(func.count(cls.id)).where(*conditions))

    @classmethod
    def count_by_status(cls):
        rows = db.session.execute(db.select(cls.status, func.count(cls.id)).group_by(cls.status)).all()
        counts = dict(rows)
        return {status: counts.get(status, 0) for status in VALID_STATUSES}

    @classmethod
    def count_by_priority(cls):
        rows = db.session.execute(db.select(cls.priority, func.count(cls.id)).group_by(cls.priority)).all()
        counts = dict(rows)
        return {label: counts.get(priority, 0) for priority, label in PRIORITY_LABELS.items()}

    @classmethod
    def count_by(cls, column):
        """Mapa {valor da coluna: quantidade de tasks} — ex.: tasks por usuário ou categoria."""
        rows = db.session.execute(db.select(column, func.count(cls.id)).group_by(column)).all()
        return dict(rows)
