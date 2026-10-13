# task-manager-api

API de Task Manager em Python/Flask usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
pip install -r requirements.txt
cp .env.example .env   # opcional: ajuste SECRET_KEY, HOST, PORT etc.
python seed.py
python app.py
```

A aplicação sobe em `http://localhost:5000`. O `seed.py` popula o banco SQLite (`tasks.db`) com usuários, categorias e tasks de exemplo — **rode-o antes do primeiro boot**, caso contrário os endpoints vão retornar listas vazias.

## Autenticação

`POST /login` retorna um `token` assinado. Envie-o como `Authorization: Bearer <token>` nas operações restritas a administradores:

- `DELETE /users/<id>`
- criar usuário com `role` diferente de `user`, ou alterar o `role` de um usuário

## Estrutura

```
app.py            # composition root (create_app) e entry point
config/           # settings (variáveis de ambiente) e constantes de domínio
models/           # entidades SQLAlchemy e consultas agregadas
validators/       # validação de payloads
controllers/      # fluxo da aplicação
services/         # relatórios e notificações
routes/           # blueprints (camada de rotas)
middlewares/      # error handler central e autenticação
utils/            # utilitários de data/percentual
seed.py           # dados iniciais
```
