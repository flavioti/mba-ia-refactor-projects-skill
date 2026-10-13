# Playbook de Refatoração

Usado na **Fase 3**. Cada seção corresponde a um anti-pattern do catálogo (mesmo ID) e traz a transformação concreta com código **antes/depois**. Os exemplos estão em Python/Flask e Node/Express; para outras stacks, aplique o mesmo princípio com a sintaxe equivalente.

## Princípios gerais

1. **Contrato preservado:** mesmas rotas, métodos, payloads, formato de resposta e status — exceto correções de segurança, que devem ser listadas no resumo.
2. **Ordem:** CRITICAL → HIGH → MEDIUM → LOW. Mudanças estruturais (AP-05/06/08) definem a nova estrutura; as demais são aplicadas já dentro dela.
3. **Sem dependências desnecessárias:** prefira o que a stack já traz (`werkzeug.security`, `itsdangerous`, `crypto` do Node). Se adicionar uma lib, atualize o manifesto.
4. **Valide incrementalmente** (import/compile) após cada bloco de mudanças.

---

## AP-01 — SQL Injection → Queries parametrizadas

**Python (sqlite3) — antes**
```python
cursor.execute("SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'")
query = "SELECT * FROM produtos WHERE 1=1"
if termo:
    query += " AND (nome LIKE '%" + termo + "%')"
```

**Depois**
```python
cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))

clauses, params = [], []
if termo:
    clauses.append("(nome LIKE ? OR descricao LIKE ?)")
    params += [f"%{termo}%", f"%{termo}%"]
if categoria:
    clauses.append("categoria = ?")
    params.append(categoria)
where = " AND ".join(clauses) or "1=1"
cursor.execute(f"SELECT * FROM produtos WHERE {where}", params)  # só fragmentos fixos interpolados
```

**Node (sqlite3) — antes / depois**
```js
db.all(`SELECT * FROM users WHERE email = '${email}'`, cb);   // antes
const user = await db.get('SELECT * FROM users WHERE email = ?', [email]);  // depois
```

Regra: valores **sempre** via parâmetros; só estruturas fixas do código (nomes de colunas de uma whitelist, `AND`) podem ser interpoladas.

---

## AP-02 — Segredos hardcoded → Módulo de configuração

**Python — antes**
```python
app.config["SECRET_KEY"] = "super-secret-dev-key"
app.run(host="0.0.0.0", port=5000, debug=True)
```

**Depois — `src/config/settings.py`**
```python
import os
import secrets


def _bool(value, default=False):
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


class Settings:
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)  # efêmera em dev
    DEBUG = _bool(os.environ.get("FLASK_DEBUG"), default=False)
    HOST = os.environ.get("HOST", "127.0.0.1")
    PORT = int(os.environ.get("PORT", "5000"))
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "app.db")
```

```python
# src/app.py
app.config.from_object(Settings)
# app.py (raiz)
app.run(host=Settings.HOST, port=Settings.PORT, debug=Settings.DEBUG)
```

**Node — antes / depois**
```js
// antes (utils.js)
const config = { dbPass: "senha_super_secreta_prod_123", paymentGatewayKey: "pk_live_123...", port: 3000 };

// depois (src/config/index.js)
const config = Object.freeze({
  port: Number(process.env.PORT) || 3000,
  dbPath: process.env.DB_PATH || ':memory:',
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
  smtpUser: process.env.SMTP_USER || '',
});
module.exports = config;
```

**`.env.example`**
```
SECRET_KEY=troque-por-um-valor-aleatorio
FLASK_DEBUG=false
PAYMENT_GATEWAY_KEY=
```

Também: remova segredos de respostas HTTP (ver AP-09). Se `python-dotenv`/`dotenv` estiver nas dependências, carregue o `.env` no entry point (`load_dotenv()` / `require('dotenv').config()`).

---

## AP-03 — Senhas inseguras → Hash adaptativo com salt

**Python — antes**
```python
self.password = hashlib.md5(pwd.encode()).hexdigest()
# ou: INSERT INTO usuarios (..., senha) VALUES (..., '" + senha + "')
# ou: SELECT * FROM usuarios WHERE email = ? AND senha = ?
```

**Depois** (`werkzeug` já vem com o Flask)
```python
from werkzeug.security import generate_password_hash, check_password_hash

def set_password(self, raw):
    self.password = generate_password_hash(raw)

def check_password(self, raw):
    return check_password_hash(self.password, raw)

# login: buscar por email e verificar em código
row = cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
if row is None or not check_password_hash(row["senha"], senha):
    raise UnauthorizedError("Email ou senha inválidos")
```

**Node — antes / depois** (`crypto` nativo, sem dependência nova)
```js
// antes
function badCrypto(pwd) { let h = ""; for (let i = 0; i < 10000; i++) h += Buffer.from(pwd).toString('base64').substring(0, 2); return h.substring(0, 10); }
let hash = badCrypto(p || "123456");

// depois (src/utils/password.js)
const crypto = require('crypto');
function hashPassword(password) {
  const salt = crypto.randomBytes(16).toString('hex');
  const hash = crypto.scryptSync(password, salt, 64).toString('hex');
  return `${salt}:${hash}`;
}
function verifyPassword(password, stored) {
  const [salt, hash] = stored.split(':');
  const candidate = crypto.scryptSync(password, salt, 64);
  return crypto.timingSafeEqual(candidate, Buffer.from(hash, 'hex'));
}
// senha ausente → erro de validação (400), nunca senha padrão
```

**Seeds:** grave as senhas de seed já com hash (mantendo os mesmos valores em texto para que o login de teste continue funcionando). Se existir um banco local antigo com senhas em texto puro, recrie-o (bancos de dev costumam estar no `.gitignore`) e registre isso no resumo.

---

## AP-04 — Endpoint sem auth → Remover ou proteger

**Antes**
```python
@app.route("/admin/query", methods=["POST"])
def executar_query():
    cursor.execute(request.get_json()["sql"])  # SQL arbitrário

role = data.get('role', 'user')                 # escalada de privilégio
return {'token': 'fake-jwt-token-' + str(user.id)}
```

**Depois**
1. **Remova** endpoints que executam SQL/comandos arbitrários — não há forma segura de mantê-los. Liste como mudança de contrato.
2. Proteja endpoints administrativos com middleware/decorator:

```python
# src/middlewares/auth.py
from functools import wraps
from flask import request, current_app
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from src.middlewares.error_handler import UnauthorizedError, ForbiddenError


def _serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="auth")

def issue_token(user):
    return _serializer().dumps({"id": user["id"], "role": user["role"]})

def require_auth(role=None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            header = request.headers.get("Authorization", "")
            if not header.startswith("Bearer "):
                raise UnauthorizedError("Token ausente")
            try:
                payload = _serializer().loads(header[7:], max_age=3600)
            except (BadSignature, SignatureExpired):
                raise UnauthorizedError("Token inválido")
            if role and payload.get("role") != role:
                raise ForbiddenError("Acesso negado")
            return fn(*args, **kwargs)
        return wrapper
    return decorator
```

```js
// Node — src/middlewares/auth.js (token via env para rotas admin)
module.exports = function requireAdmin(config) {
  return (req, res, next) => {
    const token = req.get('X-Admin-Token');
    if (!config.adminToken || token !== config.adminToken) {
      return res.status(401).json({ error: 'Unauthorized' });
    }
    next();
  };
};
```

3. Cadastro público: **ignore** `role` do payload (sempre o papel padrão); alteração de papel só por admin autenticado.
4. Token falso (`fake-jwt-token-<id>`) → token assinado (`itsdangerous`, JWT). Mantenha o campo `token` na resposta para preservar o contrato.

---

## AP-05 — God Class / God File → Separar por camada e domínio

**Antes** (arquivo de models com vários domínios, ou uma classe "Manager" com DB + rotas + pagamento)
```js
class StoreManager {
  constructor() { this.db = new sqlite3.Database(':memory:'); }
  initDb() { /* CREATE TABLE + seed */ }
  setupRoutes(app) {
    app.post('/api/orders', (req, res) => { /* validação + pagamento + SQL + resposta */ });
    app.get('/api/admin/sales-report', (req, res) => { /* SQL em loop + agregação */ });
  }
}
```

**Depois**
```
src/database/connection.js     ← new sqlite3.Database + helpers
src/database/schema.js         ← CREATE TABLE + seed
src/models/product.model.js    ← SQL de products
src/models/order.model.js      ← SQL de orders
src/services/order.service.js  ← regra de pagamento + pedido (transação)
src/controllers/order.controller.js
src/routes/order.routes.js     ← router.post('/orders', ...)
src/app.js                     ← composição
```

Passos:
1. Liste cada função/método do God File e classifique: dados, regra, rota, config, seed.
2. Crie um módulo por **camada × domínio** e mova o código (sem reescrever a lógica ainda).
3. Substitua as chamadas antigas pelas novas e apague o arquivo original.
4. Só então aplique as demais correções (AP-01, AP-10, …) dentro da nova estrutura.

---

## AP-06 — Fat Controller → Controller fino + Model/Service

**Antes** (handler de rota com regra e ORM inline)
```python
@task_bp.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    # 60 linhas: validação, lookup de user/category, parse de data, tags, db.session...
```

**Depois**
```python
# src/views/task_routes.py
@task_bp.route('/tasks', methods=['POST'])
def create_task():
    task = task_controller.create(request.get_json(silent=True))
    return jsonify(task), 201

# src/controllers/task_controller.py
def create(payload):
    data = validate_task_payload(payload, partial=False)   # AP-12
    task = task_service.create(data)                       # regra + persistência
    return task.to_dict()

# src/services/task_service.py
def create(data):
    if data.get("user_id") and not db.session.get(User, data["user_id"]):
        raise NotFoundError("Usuário não encontrado")
    task = Task(**data)
    db.session.add(task)
    db.session.commit()
    return task
```

Regra prática: o handler de rota tem ≤ ~10 linhas — extrai entrada, chama controller, devolve resposta.

---

## AP-07 — Estado global mutável → Escopo por requisição / injeção

**Python — antes**
```python
db_connection = None
def get_db():
    global db_connection
    if db_connection is None:
        db_connection = sqlite3.connect(db_path, check_same_thread=False)
    return db_connection
```

**Depois** (conexão por requisição via `flask.g`)
```python
import sqlite3
from flask import g, current_app

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE_PATH"])
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_app(app):
    app.teardown_appcontext(close_db)
```

**Node — antes / depois**
```js
// antes
let globalCache = {};
let totalRevenue = 0;
module.exports = { globalCache, totalRevenue };

// depois: estado explícito, encapsulado e injetado (ou removido se não é usado)
function createCache({ maxEntries = 1000 } = {}) {
  const store = new Map();
  return {
    set(key, value) {
      if (store.size >= maxEntries) store.delete(store.keys().next().value);
      store.set(key, value);
    },
    get: (key) => store.get(key),
  };
}
```

Valores derivados (ex.: receita total) devem ser **calculados do banco**, não mantidos em variável global.

---

## AP-08 — Acoplamento forte → Composition root + injeção

**Antes**
```python
# controllers.py
from database import get_db
def health_check():
    db = get_db()
    ...
```

**Depois — Python (`create_app` como composition root)**
```python
# src/app.py
def create_app(settings=Settings):
    app = Flask(__name__)
    app.config.from_object(settings)
    database.init_app(app)
    register_error_handlers(app)
    app.register_blueprint(produto_routes.bp)
    app.register_blueprint(usuario_routes.bp)
    app.register_blueprint(pedido_routes.bp)
    return app
```

**Depois — Node (factories)**
```js
// src/app.js
const db = await createConnection(config.dbPath);
await initSchema(db);

const courseModel = createCourseModel(db);
const userModel = createUserModel(db);
const checkoutService = createCheckoutService({ db, courseModel, userModel, config });
const checkoutController = createCheckoutController({ checkoutService });

app.use('/api', createCheckoutRouter({ checkoutController }));
app.use(errorHandler);
```

Benefício: em testes, injeta-se um banco em memória ou um gateway falso sem alterar o código de produção.

---

## AP-09 — Dados sensíveis expostos → Serializer seguro, logs mascarados, erro genérico

**Antes**
```python
def to_dict(self):
    return {'id': self.id, 'email': self.email, 'password': self.password}

return jsonify({"status": "ok", "secret_key": "super-secret...", "debug": True})
return jsonify({"erro": str(e)}), 500
```
```js
console.log(`Processando cartão ${cc} na chave ${config.paymentGatewayKey}`);
```

**Depois**
```python
def to_dict(self):
    return {'id': self.id, 'name': self.name, 'email': self.email, 'role': self.role}

return jsonify({"status": "ok", "database": "connected", "versao": "1.0.0"})
# erros 500: mensagem genérica ao cliente, detalhe só no log (ver AP-13)
```
```js
const masked = `****${card.slice(-4)}`;
logger.info(`Processando pagamento do cartão ${masked}`);
```

---

## AP-10 — N+1 → JOIN, eager loading, agregação

**SQL cru — antes**
```python
for row in cursor.execute("SELECT * FROM pedidos").fetchall():
    itens = db.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"])).fetchall()
    for item in itens:
        prod = db.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"])).fetchone()
```

**Depois**
```python
rows = db.execute("""
    SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,
           i.produto_id, i.quantidade, i.preco_unitario,
           COALESCE(pr.nome, 'Desconhecido') AS produto_nome
    FROM pedidos p
    LEFT JOIN itens_pedido i ON i.pedido_id = p.id
    LEFT JOIN produtos pr    ON pr.id = i.produto_id
    WHERE (:usuario_id IS NULL OR p.usuario_id = :usuario_id)
    ORDER BY p.id
""", {"usuario_id": usuario_id}).fetchall()

pedidos = {}
for r in rows:
    pedido = pedidos.setdefault(r["id"], {
        "id": r["id"], "usuario_id": r["usuario_id"], "status": r["status"],
        "total": r["total"], "criado_em": r["criado_em"], "itens": [],
    })
    if r["produto_id"] is not None:
        pedido["itens"].append({
            "produto_id": r["produto_id"], "produto_nome": r["produto_nome"],
            "quantidade": r["quantidade"], "preco_unitario": r["preco_unitario"],
        })
return list(pedidos.values())
```

**SQLAlchemy — antes / depois**
```python
# antes
for t in Task.query.all():
    user = User.query.get(t.user_id)

# depois
from sqlalchemy.orm import joinedload
tasks = db.session.execute(
    db.select(Task).options(joinedload(Task.user), joinedload(Task.category))
).scalars().all()

# contagens por grupo: 1 query
counts = dict(db.session.execute(
    db.select(Task.category_id, db.func.count(Task.id)).group_by(Task.category_id)
).all())
```

---

## AP-11 — Sem transação → Operação atômica

**Python sqlite3 — antes**
```python
cursor.execute("INSERT INTO pedidos ...")
for item in itens:
    cursor.execute("INSERT INTO itens_pedido ...")
    cursor.execute("UPDATE produtos SET estoque = estoque - ...")
db.commit()
```

**Depois**
```python
def criar_pedido(db, usuario_id, itens):
    produtos = _carregar_e_validar_estoque(db, itens)   # valida TUDO antes de escrever
    with db:                                            # BEGIN … COMMIT / ROLLBACK automático
        cur = db.execute("INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
                         (usuario_id, total))
        pedido_id = cur.lastrowid
        for item in itens:
            db.execute("INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
                       (pedido_id, item["produto_id"], item["quantidade"], produtos[item["produto_id"]]["preco"]))
            db.execute("UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
                       (item["quantidade"], item["produto_id"]))
    return pedido_id
```

**Node — depois** (com helpers promisificados, ver AP-15)
```js
async function withTransaction(db, work) {
  await db.run('BEGIN');
  try {
    const result = await work();
    await db.run('COMMIT');
    return result;
  } catch (err) {
    await db.run('ROLLBACK');
    throw err;
  }
}
```

**Exclusão com dependentes:** apague filhos na mesma transação (ou use FK `ON DELETE CASCADE` com `PRAGMA foreign_keys = ON`).

---

## AP-12 — Validação ausente/duplicada → Validador único por entidade

**Antes** (duas cópias divergentes em create/update)
```python
if "nome" not in dados: return jsonify({"erro": "Nome é obrigatório"}), 400
if preco < 0: return jsonify({"erro": "Preço não pode ser negativo"}), 400   # quebra se preco for str
```

**Depois**
```python
# src/validators/produto_validator.py
from src.config.settings import CATEGORIAS_VALIDAS, NOME_MIN, NOME_MAX
from src.middlewares.error_handler import ValidationError

def validar_produto(dados):
    if not isinstance(dados, dict):
        raise ValidationError("Dados inválidos")
    for campo in ("nome", "preco", "estoque"):
        if campo not in dados:
            raise ValidationError(f"{campo.capitalize()} é obrigatório")
    nome = dados["nome"]
    if not isinstance(nome, str) or not NOME_MIN <= len(nome) <= NOME_MAX:
        raise ValidationError("Nome inválido")
    if not isinstance(dados["preco"], (int, float)) or dados["preco"] < 0:
        raise ValidationError("Preço não pode ser negativo")
    if not isinstance(dados["estoque"], int) or dados["estoque"] < 0:
        raise ValidationError("Estoque não pode ser negativo")
    categoria = dados.get("categoria", "geral")
    if categoria not in CATEGORIAS_VALIDAS:
        raise ValidationError(f"Categoria inválida. Válidas: {CATEGORIAS_VALIDAS}")
    return {"nome": nome, "descricao": dados.get("descricao", ""), "preco": dados["preco"],
            "estoque": dados["estoque"], "categoria": categoria}
```

Usado por **create e update**. Se o projeto já declara `marshmallow`/`pydantic`/`joi`/`zod`, use a biblioteca em vez de validação manual. Preserve as mensagens de erro originais quando possível.

---

## AP-13 — Erros genéricos → Exceções de domínio + handler central

**Antes** (repetido em todos os handlers)
```python
try:
    ...
except Exception as e:
    return jsonify({"erro": str(e)}), 500
```

**Depois — Flask (`src/middlewares/error_handler.py`)**
```python
import logging
from flask import jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)

class AppError(Exception):
    status_code = 400
    def __init__(self, message):
        super().__init__(message)
        self.message = message

class ValidationError(AppError):   status_code = 400
class UnauthorizedError(AppError): status_code = 401
class ForbiddenError(AppError):    status_code = 403
class NotFoundError(AppError):     status_code = 404
class ConflictError(AppError):     status_code = 409

def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(err):
        return jsonify({"erro": err.message, "sucesso": False}), err.status_code

    @app.errorhandler(HTTPException)          # 404, 405, 400 do próprio Flask
    def handle_http_error(err):
        return jsonify({"erro": err.description, "sucesso": False}), err.code

    @app.errorhandler(Exception)
    def handle_unexpected(err):
        logger.exception("Erro inesperado")
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500
```

> Use a chave de erro que o projeto já usa (`"erro"` ou `"error"`) para preservar o contrato.

**Depois — Express**
```js
// src/middlewares/asyncHandler.js
module.exports = (fn) => (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);

// src/middlewares/errorHandler.js
class AppError extends Error {
  constructor(message, statusCode = 400) { super(message); this.statusCode = statusCode; }
}
function errorHandler(err, req, res, next) {
  if (err instanceof AppError) return res.status(err.statusCode).send(err.message);
  logger.error(err);
  res.status(500).send('Erro interno');
}
module.exports = { AppError, errorHandler };
```

Registre o error handler **por último** no entry point. Em Python, troque todo `except:` por exceções específicas.

---

## AP-14 — APIs deprecated → Equivalentes modernos

**Antes**
```python
from datetime import datetime
created_at = db.Column(db.DateTime, default=datetime.utcnow)
task = Task.query.get(task_id)
```
```js
const buf = new Buffer(str);
const { pathname } = url.parse(req.url);
app.use(bodyParser.json());
```

**Depois**
```python
from datetime import datetime, timezone

def utcnow():
    return datetime.now(timezone.utc)

created_at = db.Column(db.DateTime, default=utcnow)   # passa a função, não o resultado
task = db.session.get(Task, task_id)
if task is None:
    raise NotFoundError("Task não encontrada")
```
```js
const buf = Buffer.from(str);
const { pathname } = new URL(req.url, `http://${req.headers.host}`);
app.use(express.json());
```

Atenção ao comparar datas: `datetime.now(timezone.utc)` é *aware*; valores lidos do SQLite costumam ser *naive*. Normalize antes de comparar (ex.: `due.replace(tzinfo=timezone.utc)` se o valor for naive).

---

## AP-15 — Callback hell → async/await

**Antes**
```js
this.db.get("SELECT * FROM courses WHERE id = ?", [cid], (err, course) => {
  this.db.get("SELECT id FROM users WHERE email = ?", [e], (err, user) => {
    this.db.run("INSERT INTO enrollments ...", [userId, cid], function (err) {
      self.db.run("INSERT INTO payments ...", [this.lastID, ...], function (err) {
        res.status(200).json({ msg: "Sucesso", enrollment_id: enrId });
      });
    });
  });
});
```

**Depois**
```js
// src/database/connection.js
const sqlite3 = require('sqlite3');

function createConnection(path) {
  const raw = new sqlite3.Database(path);
  return {
    run: (sql, params = []) => new Promise((resolve, reject) =>
      raw.run(sql, params, function (err) { err ? reject(err) : resolve({ lastID: this.lastID, changes: this.changes }); })),
    get: (sql, params = []) => new Promise((resolve, reject) =>
      raw.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)))),
    all: (sql, params = []) => new Promise((resolve, reject) =>
      raw.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)))),
    close: () => new Promise((resolve, reject) => raw.close((err) => (err ? reject(err) : resolve()))),
  };
}

// src/services/checkout.service.js
async function checkout({ name, email, password, courseId, card }) {
  const course = await courseModel.findActiveById(courseId);
  if (!course) throw new AppError('Curso não encontrado', 404);
  if (!paymentGateway.approve(card)) throw new AppError('Pagamento recusado', 400);

  return withTransaction(db, async () => {
    const userId = (await userModel.findByEmail(email))?.id
      ?? (await userModel.create({ name, email, password })).lastID;
    const { lastID: enrollmentId } = await enrollmentModel.create(userId, courseId);
    await paymentModel.create(enrollmentId, course.price, PAYMENT_STATUS.PAID);
    await auditModel.log(`Checkout curso ${courseId} por ${userId}`);
    return enrollmentId;
  });
}
```

Para vários itens independentes, use `Promise.all` em vez de contadores manuais.

---

## AP-16 — Lógica duplicada → Fonte única

**Antes** (mesmo cálculo copiado em várias rotas)
```python
if t.due_date:
    if t.due_date < datetime.utcnow():
        if t.status != 'done' and t.status != 'cancelled':
            task_data['overdue'] = True
```

**Depois**
```python
# models/task.py
CLOSED_STATUSES = ("done", "cancelled")

def is_overdue(self, now=None):
    now = now or utcnow()
    return bool(self.due_date) and self.due_date < now and self.status not in CLOSED_STATUSES

def to_dict(self):
    return {..., "overdue": self.is_overdue()}

# rotas/controllers
return [t.to_dict() for t in tasks]
```

Funções quase idênticas (`get_all_orders` / `get_orders_by_customer`) viram **uma** com filtro opcional (ver AP-10).

---

## AP-17 — Magic numbers → Constantes nomeadas

**Antes**
```python
if faturamento > 10000:   desconto = faturamento * 0.1
elif faturamento > 5000:  desconto = faturamento * 0.05
elif faturamento > 1000:  desconto = faturamento * 0.02
```
```js
let status = cc.startsWith("4") ? "PAID" : "DENIED";
```

**Depois**
```python
# src/config/settings.py
FAIXAS_DESCONTO = ((10000, 0.10), (5000, 0.05), (1000, 0.02))  # (faturamento mínimo, taxa)

def calcular_desconto(faturamento):
    for minimo, taxa in FAIXAS_DESCONTO:
        if faturamento > minimo:
            return faturamento * taxa
    return 0
```
```js
// src/config/constants.js
const PAYMENT_STATUS = Object.freeze({ PAID: 'PAID', DENIED: 'DENIED' });
const APPROVED_CARD_PREFIX = '4'; // regra do gateway simulado
```

Se o projeto já tem constantes declaradas (ex.: `VALID_STATUSES`), **use-as** em vez de criar novas.

---

## AP-18 — print/console.log → Logger

**Antes**
```python
print("Login bem-sucedido: " + email)
print("ENVIANDO EMAIL: Pedido " + str(pedido_id))
```

**Depois**
```python
# src/app.py (create_app)
logging.basicConfig(level=logging.DEBUG if settings.DEBUG else logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")

# módulos
logger = logging.getLogger(__name__)
logger.info("Login bem-sucedido para usuario_id=%s", usuario["id"])   # sem dados pessoais
notification_service.pedido_criado(pedido_id, usuario_id)            # efeito em service próprio
```
```js
// src/utils/logger.js — wrapper mínimo sem dependência
const levels = ['debug', 'info', 'warn', 'error'];
module.exports = Object.fromEntries(levels.map((lvl) =>
  [lvl, (...args) => console[lvl === 'debug' ? 'log' : lvl](`[${new Date().toISOString()}] ${lvl.toUpperCase()}`, ...args)]));
```

Mensagens de inicialização do servidor podem permanecer, via logger.

---

## AP-19 — Nomes ruins → Nomes descritivos

**Antes**
```js
let u = req.body.usr;
let e = req.body.eml;
let cc = req.body.card;
```
```python
id = models.criar_produto(...)   # shadowing de builtin
```

**Depois**
```js
const { usr: name, eml: email, pwd: password, c_id: courseId, card } = req.body;  // contrato preservado
```
```python
produto_id = produto_model.criar(...)
```

Campos do payload/resposta **não** são renomeados (mudaria o contrato); renomeie apenas identificadores internos. Funções com nomes enganosos (`badCrypto`) são substituídas, não apenas renomeadas.

---

## AP-20 — Código morto → Remover

**Antes**
```python
import os, sys, json, datetime   # só datetime é usado
from utils.helpers import format_date, calculate_percentage   # nunca chamados
```

**Depois**
```python
import datetime
```

Remova também: funções/helpers sem chamadas, variáveis atribuídas e não lidas, exports não importados, arquivos substituídos pela refatoração. Antes de remover um helper, confirme com Grep que não há uso — ou **passe a usá-lo** se ele resolve uma duplicação (AP-16).

---

## AP-21 — Condicionais verbosas → Expressões diretas

**Antes**
```python
def is_admin(self):
    if self.role == 'admin':
        return True
    else:
        return False

completed = 0
for t in tasks:
    if t.status == 'done':
        completed = completed + 1

if type(tags) == list:
    ...
```

**Depois**
```python
def is_admin(self):
    return self.role == "admin"

completed = sum(1 for t in tasks if t.status == "done")   # ou COUNT/GROUP BY no banco

if isinstance(tags, list):
    ...
```

Prefira guard clauses (`if not x: raise ...`) a `if` aninhados.
