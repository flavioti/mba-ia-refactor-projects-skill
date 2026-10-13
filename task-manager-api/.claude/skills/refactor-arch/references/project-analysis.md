# Análise de Projeto — Heurísticas

Usado na **Fase 1**. Objetivo: descrever a stack e a arquitetura atual **com base em evidências** (arquivos, dependências, imports), nunca por suposição. Também define os comandos de instalação/execução usados na validação da Fase 3.

## 1. Inventário de arquivos

```bash
# arquivos-fonte, ignorando dependências, builds e a própria skill
find . -type f \( -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.mjs" -o -name "*.cjs" \
  -o -name "*.rb" -o -name "*.php" -o -name "*.java" -o -name "*.go" -o -name "*.cs" \) \
  -not -path "*/node_modules/*" -not -path "*/.venv/*" -not -path "*/venv/*" \
  -not -path "*/__pycache__/*" -not -path "*/.git/*" -not -path "*/.claude/*" \
  -not -path "*/dist/*" -not -path "*/build/*" | sort

# total de linhas
... | xargs wc -l
```

- Conte **apenas** arquivos-fonte de aplicação (inclua scripts como `seed.py`, mas cite-os como auxiliares).
- Arquivos `__init__.py` vazios contam como arquivo, mas não como "lógica".

## 2. Detecção de linguagem

| Evidência | Linguagem |
|---|---|
| `requirements.txt`, `pyproject.toml`, `Pipfile`, `setup.py`, arquivos `.py` | Python |
| `package.json` + `.js`/`.mjs`/`.cjs` | JavaScript (Node.js) |
| `package.json` + `tsconfig.json`/`.ts` | TypeScript (Node.js) |
| `Gemfile`, `.rb` | Ruby |
| `composer.json`, `.php` | PHP |
| `pom.xml`, `build.gradle`, `.java` | Java |
| `go.mod`, `.go` | Go |
| `*.csproj`, `.cs` | C# |

Versão: `python_requires`/`.python-version`/`runtime.txt`; `engines.node` no `package.json`/`.nvmrc`. Se não declarada, informe "não declarada" (não invente).

## 3. Detecção de framework

Procure no manifesto **e** confirme nos imports:

| Linguagem | Dependência / import | Framework |
|---|---|---|
| Python | `flask` / `from flask import Flask` | Flask |
| Python | `fastapi` / `from fastapi import FastAPI` | FastAPI |
| Python | `django` / `settings.py`, `urls.py`, `manage.py` | Django |
| Node | `express` / `require('express')`, `from 'express'` | Express |
| Node | `fastify`, `koa`, `@nestjs/core`, `@hapi/hapi` | Fastify, Koa, NestJS, Hapi |
| Ruby | `rails`, `sinatra` | Rails, Sinatra |
| PHP | `laravel/framework`, `slim/slim` | Laravel, Slim |

Versão: use a do manifesto (`flask==3.1.1`, `"express": "^4.18.2"`). Para faixas (`^4.18.2`), informe a faixa ou a versão resolvida no lockfile, se existir.

Dependências relevantes a listar: extensões do framework (CORS, ORM, validação, auth), drivers de banco, libs de HTTP/email/pagamento. Anote dependências **declaradas mas não usadas** (ex.: `marshmallow`, `python-dotenv`) — viram evidência para AP-12/AP-02/AP-20.

## 4. Detecção de banco de dados e forma de acesso

| Evidência | Banco / acesso |
|---|---|
| `import sqlite3`, `sqlite3.connect(` | SQLite — SQL cru (Python) |
| `require('sqlite3')`, `new sqlite3.Database(` | SQLite — SQL cru (Node) |
| `flask_sqlalchemy`, `SQLAlchemy()`, `db.Model` | ORM SQLAlchemy (banco pela `SQLALCHEMY_DATABASE_URI`) |
| `psycopg2`, `pg`, `mysql`, `mysql2`, `pymongo`, `mongoose` | PostgreSQL / MySQL / MongoDB |
| `sequelize`, `typeorm`, `prisma`, `knex` | ORM/query builder Node |

- `':memory:'` → banco em memória (dados perdidos a cada restart — anote).
- **Tabelas/entidades:** extraia de `CREATE TABLE`, `__tablename__`, classes `db.Model`, schemas do ORM.

## 5. Inferência do domínio

Combine nomes de tabelas, entidades e rotas:
- `products`, `orders`, `order_items`, `cart` → E-commerce
- `courses`, `lessons`, `enrollments` → LMS / plataforma de ensino
- `tasks`, `projects`, `boards` → gestão de tarefas/projetos
- `accounts`, `transactions`, `invoices` → financeiro/faturamento
- `posts`, `comments`, `tags` → blog/CMS
- `patients`, `appointments` → agendamento/saúde

Os nomes podem estar em qualquer idioma (ex.: `pedidos`, `usuarios`). Use o significado, não a grafia. Rotas como `/checkout`, `/login` e `/reports` complementam a inferência.

Descreva em uma linha: tipo de sistema + entidades principais.

## 6. Inventário de endpoints

| Framework | Padrões de busca |
|---|---|
| Flask | `@app.route(`, `@<bp>.route(`, `app.add_url_rule(`, `Blueprint(` (+ `url_prefix` no `register_blueprint`) |
| FastAPI | `@app.get(`/`post`/`put`/`delete`, `APIRouter(` |
| Express | `app.get(`/`post`/`put`/`patch`/`delete`, `router.<método>(`, `app.use('/prefixo', router)` |

Registre cada endpoint como `MÉTODO /caminho → handler (arquivo:linha)`. Considere prefixos de blueprint/router. Esse inventário é o roteiro de validação da Fase 3.

## 7. Classificação da arquitetura

| Classificação | Sinais |
|---|---|
| **Monolito desestruturado** | ≤ 5 arquivos; SQL, regras e rotas misturados; classe/arquivo "faz-tudo" |
| **Camadas parciais** | Pastas `models/`, `routes/`, `services/`, `utils/` existem, mas rotas acessam o banco direto, services/helpers são pouco usados, sem config/error handler centrais |
| **MVC / camadas completas** | Models, controllers e rotas separados; config externa; composition root; error handler central |

Justifique a classificação em uma linha com fatos (ex.: "um único arquivo de classe concentra conexão, seed, rotas e regra de pagamento").

## 8. Entry point e execução

| Stack | Entry point | Instalação | Execução |
|---|---|---|---|
| Python/Flask | arquivo com `app.run(` ou `create_app()`; `FLASK_APP` | `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt` | `.venv/bin/python app.py` |
| Node/Express | `scripts.start` ou `main` no `package.json`; arquivo com `app.listen(` | `npm install` | `npm start` (ou `node <main>`) |

- **Porta:** procure em `app.run(port=...)`, `app.listen(...)`, config ou env. Padrões: Flask 5000, Express 3000.
- **Seed:** procure scripts (`seed.py`, `npm run seed`) ou seed automático no boot.
- Se a porta já estiver em uso, use outra via env/argumento — não mate processos que você não iniciou.

## 9. Execução e validação (usado na Fase 3)

```bash
# subir em background e guardar o PID (exemplo Python)
.venv/bin/python app.py > /tmp/app.log 2>&1 &
APP_PID=$!
# aguardar até responder (máx. ~15s)
for i in $(seq 1 30); do curl -s -o /dev/null http://localhost:5000/ && break; sleep 0.5; done

# chamar endpoints
curl -s -w "\n%{http_code}\n" http://localhost:5000/health
curl -s -w "\n%{http_code}\n" -X POST http://localhost:5000/recurso \
     -H "Content-Type: application/json" -d '{"campo":"valor"}'

# encerrar
kill $APP_PID
```

- Use dados de seed existentes para montar requisições válidas (IDs, emails, senhas de teste).
- Se houver `api.http` ou exemplos no README do projeto, use-os como fonte das requisições.
- Verifique o log (`/tmp/app.log`) por exceções e `DeprecationWarning`/`LegacyAPIWarning` (Python: rode com `-W default` para exibi-las).
- Bancos SQLite em arquivo criados durante o teste: remova-os ao final se não existiam antes (ou se estão no `.gitignore` e foram gerados pela validação).
