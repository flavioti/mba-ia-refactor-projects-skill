"""Script para popular o banco com dados iniciais"""
from datetime import timedelta

from app import app
from database import db
from models.category import Category
from models.task import Task
from models.user import User
from utils.datetime_utils import utcnow

USERS = [
    ("João Silva", "joao@email.com", "1234", "admin"),
    ("Maria Santos", "maria@email.com", "abcd", "user"),
    ("Pedro Oliveira", "pedro@email.com", "pass", "manager"),
]

CATEGORIES = [
    ("Backend", "Tarefas de backend", "#3498db"),
    ("Frontend", "Tarefas de frontend", "#2ecc71"),
    ("DevOps", "Tarefas de infraestrutura", "#e74c3c"),
    ("Bug", "Correção de bugs", "#e67e22"),
]


def seed_data():
    with app.app_context():
        for model in (Task, User, Category):
            db.session.execute(db.delete(model))
        db.session.commit()

        users = []
        for name, email, password, role in USERS:
            user = User(name=name, email=email, role=role)
            user.set_password(password)
            users.append(user)
        categories = [Category(name=n, description=d, color=c) for n, d, c in CATEGORIES]
        db.session.add_all(users + categories)
        db.session.commit()

        u1, u2, u3 = users
        c1, c2, c3, c4 = categories
        now = utcnow()
        tasks = [
            Task(title='Implementar autenticação JWT', description='Adicionar autenticação real com JWT', status='pending', priority=1, user_id=u1.id, category_id=c1.id, due_date=now - timedelta(days=3)),
            Task(title='Criar tela de login', description='Tela de login responsiva', status='in_progress', priority=2, user_id=u2.id, category_id=c2.id, due_date=now + timedelta(days=5)),
            Task(title='Configurar CI/CD', description='Pipeline com GitHub Actions', status='done', priority=2, user_id=u3.id, category_id=c3.id, tags='devops,ci,github'),
            Task(title='Corrigir bug no filtro de busca', description='Filtro não funciona com caracteres especiais', status='pending', priority=1, user_id=u1.id, category_id=c4.id, due_date=now - timedelta(days=1)),
            Task(title='Adicionar paginação na API', description='Endpoints retornam todos os registros', status='pending', priority=3, user_id=u1.id, category_id=c1.id, due_date=now + timedelta(days=10)),
            Task(title='Escrever testes unitários', description='Cobertura mínima de 80%', status='pending', priority=2, user_id=u2.id, category_id=c1.id),
            Task(title='Documentar API com Swagger', description='Gerar documentação automática', status='cancelled', priority=4, user_id=u3.id, category_id=c1.id),
            Task(title='Refatorar models', description='Melhorar organização dos models', status='in_progress', priority=3, user_id=u2.id, category_id=c1.id, tags='refactor,tech-debt'),
            Task(title='Configurar monitoramento', description='Prometheus + Grafana', status='pending', priority=4, user_id=u3.id, category_id=c3.id, due_date=now + timedelta(days=20)),
            Task(title='Melhorar validações de input', description='Usar marshmallow ou pydantic', status='pending', priority=3, user_id=u1.id, category_id=c1.id, tags='improvement,validation'),
        ]
        db.session.add_all(tasks)
        db.session.commit()

        print("Seed concluído com sucesso!")
        print(f"  {len(users)} usuários")
        print(f"  {len(categories)} categorias")
        print(f"  {len(tasks)} tasks")


if __name__ == '__main__':
    seed_data()
