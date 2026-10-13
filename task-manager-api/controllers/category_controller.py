from database import db
from middlewares.error_handler import NotFoundError
from models.category import Category
from models.task import Task
from validators.category_validator import validate_category_create, validate_category_update


def list_categories():
    categories = db.session.execute(db.select(Category).order_by(Category.id)).scalars().all()
    task_counts = Task.count_by(Task.category_id)
    return [{**category.to_dict(), "task_count": task_counts.get(category.id, 0)} for category in categories]


def create_category(payload):
    category = Category(**validate_category_create(payload))
    db.session.add(category)
    db.session.commit()
    return category.to_dict()


def update_category(category_id, payload):
    category = _get_category_or_404(category_id)
    for field, value in validate_category_update(payload).items():
        setattr(category, field, value)
    db.session.commit()
    return category.to_dict()


def delete_category(category_id):
    category = _get_category_or_404(category_id)
    db.session.delete(category)
    db.session.commit()


def _get_category_or_404(category_id):
    category = db.session.get(Category, category_id)
    if category is None:
        raise NotFoundError("Categoria não encontrada")
    return category
