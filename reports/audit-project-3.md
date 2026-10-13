================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.0.0
Files:   15 analyzed | ~1158 lines of code
Date:    2026-10-13

## Summary
CRITICAL: 4 | HIGH: 3 | MEDIUM: 6 | LOW: 5

| # | Severity | Anti-pattern | Location |
|---|---|---|---|
| F-01 | CRITICAL | Credenciais e segredos hardcoded (AP-02) | `app.py:13`, `app.py:34`, `services/notification_service.py:9-10` +1 |
| F-02 | CRITICAL | Armazenamento inseguro de senhas (AP-03) | `models/user.py:29`, `models/user.py:32`, `seed.py:19` +2 |
| F-03 | CRITICAL | Endpoint sensível sem autenticação/autorização (AP-04) | `routes/user_routes.py:52`, `routes/user_routes.py:210`, `routes/user_routes.py:119-122` +1 |
| F-04 | CRITICAL | God File (AP-05) | `routes/report_routes.py:1-223` |
| F-05 | HIGH | Fat Controller (AP-06) | `routes/task_routes.py:85-154`, `routes/report_routes.py:12-101`, `routes/user_routes.py:42-90` +5 |
| F-06 | HIGH | Acoplamento forte sem injeção de dependência (AP-08) | `app.py:9-31`, `services/notification_service.py:15`, `seed.py:2` |
| F-07 | HIGH | Exposição de dados sensíveis em respostas (AP-09) | `models/user.py:21`, `routes/user_routes.py:33`, `routes/user_routes.py:209` +2 |
| F-08 | MEDIUM | Queries N+1 (AP-10) | `routes/task_routes.py:41-51`, `routes/report_routes.py:55-56`, `routes/report_routes.py:161-163` +3 |
| F-09 | MEDIUM | Operação multi-etapa sem transação / registros órfãos (AP-11) | `routes/report_routes.py:211-223` |
| F-10 | MEDIUM | Validação de entrada ausente, duplicada ou inconsistente (AP-12) | `routes/task_routes.py:113`, `routes/report_routes.py:196-197`, `routes/task_routes.py:261` +5 |
| F-11 | MEDIUM | Tratamento de erro genérico e não centralizado (AP-13) | `routes/task_routes.py:62`, `routes/user_routes.py:130`, `routes/report_routes.py:186` +9 |
| F-12 | MEDIUM | Uso de APIs deprecated (AP-14) | `models/task.py:15-16`, `routes/task_routes.py:67`, `routes/report_routes.py:35` +30 |
| F-13 | MEDIUM | Lógica de negócio duplicada (AP-16) | `routes/task_routes.py:30-39`, `routes/user_routes.py:171-180`, `routes/task_routes.py:17-28` +6 |
| F-14 | LOW | Magic numbers e strings (AP-17) | `routes/task_routes.py:110`, `routes/user_routes.py:71`, `utils/helpers.py:110-116` +8 |
| F-15 | LOW | `print` como mecanismo de logging (AP-18) | `routes/task_routes.py:149`, `routes/user_routes.py:83`, `services/notification_service.py:21` +8 |
| F-16 | LOW | Nomenclatura ruim (AP-19) | `routes/report_routes.py:24-28`, `models/category.py:14`, `models/task.py:45` +1 |
| F-17 | LOW | Código morto e imports não utilizados (AP-20) | `app.py:7`, `routes/task_routes.py:7`, `utils/helpers.py:1-116` +7 |
| F-18 | LOW | Condicionais verbosas / aninhamento excessivo (AP-21) | `models/task.py:50-60`, `models/user.py:34-38`, `routes/task_routes.py:141` +5 |

## Findings

### F-01 [CRITICAL] Credenciais e segredos hardcoded
Catalog: AP-02
File:
- app.py:13
- app.py:34
- services/notification_service.py:9-10
- requirements.txt:6
Evidence:
```python
app.config['SECRET_KEY'] = 'supe***'
app.run(debug=True, host='0.0.0.0', port=5000)
self.email_password = 'senh***'
```
Description: `SECRET_KEY` e credenciais SMTP (usuário/senha) fixos no código; `debug=True` fixo com bind em `0.0.0.0`. `python-dotenv` é declarado mas nunca usado — não há leitura de ambiente em nenhum lugar.
Impact: Qualquer pessoa com acesso ao repositório obtém a chave de assinatura de sessão e a senha do e-mail; o debugger do Werkzeug exposto em rede permite execução remota de código.
Recommendation: Módulo `config/` lendo variáveis de ambiente, `DEBUG` controlado por env, `.env.example`. Ver playbook AP-02.

### F-02 [CRITICAL] Armazenamento inseguro de senhas
Catalog: AP-03
File:
- models/user.py:29
- models/user.py:32
- seed.py:19
- seed.py:26
- seed.py:33
Evidence:
```python
self.password = hashlib.md5(pwd.encode()).hexdigest()
return self.password == hashlib.md5(pwd.encode()).hexdigest()
```
Description: Senhas armazenadas com MD5 sem salt e verificadas com comparação `==` (não constante). Seeds usam senhas triviais (`1234`, `abcd`, `pass`) e a política mínima é de 4 caracteres.
Impact: Vazamento do banco revela as senhas em segundos (rainbow tables); timing attack na comparação.
Recommendation: `werkzeug.security.generate_password_hash`/`check_password_hash` (pbkdf2/scrypt com salt). Ver playbook AP-03.

### F-03 [CRITICAL] Endpoint sensível sem autenticação/autorização
Catalog: AP-04
File:
- routes/user_routes.py:52
- routes/user_routes.py:71-72
- routes/user_routes.py:119-122
- routes/user_routes.py:210
- routes/user_routes.py:134-151
Evidence:
```python
role = data.get('role', 'user')
...
'token': 'fake-jwt-token-' + str(user.id)
```
Description: `POST /users` aceita `role` (inclusive `admin`) do payload público; `PUT /users/<id>` permite trocar `role` e `active`; `DELETE /users/<id>` apaga usuário e tasks; o login devolve um token previsível que nenhuma rota verifica.
Impact: Qualquer cliente anônimo cria um admin, promove contas, desativa ou exclui usuários; o "token" pode ser forjado para qualquer id.
Recommendation: Não aceitar `role` no cadastro público (forçar `user`); introduzir autenticação real e checagem de papel nas rotas administrativas. Ver playbook AP-04.

### F-04 [CRITICAL] God File
Catalog: AP-05
File:
- routes/report_routes.py:1-223
Evidence:
```python
report_bp = Blueprint('reports', __name__)
@report_bp.route('/reports/summary', methods=['GET'])
@report_bp.route('/categories', methods=['POST'])
```
Description: O blueprint de relatórios mistura dois domínios (relatórios e CRUD completo de categorias) e, para ambos, concentra definição de rotas, consultas ORM, regras de negócio (atraso, taxa de conclusão), validação de entrada e montagem da resposta.
Impact: Mudanças em categorias e relatórios colidem no mesmo arquivo; impossível testar regras sem HTTP + banco.
Recommendation: Separar por domínio (`category` e `report`) e por camada (rota → controller → model/service). Ver playbook AP-05.

### F-05 [HIGH] Fat Controller
Catalog: AP-06
File:
- routes/task_routes.py:11-63
- routes/task_routes.py:85-154
- routes/task_routes.py:156-223
- routes/task_routes.py:273-299
- routes/user_routes.py:42-90
- routes/user_routes.py:92-132
- routes/report_routes.py:12-101
- routes/report_routes.py:103-155
Evidence:
```python
if status not in ['pending', 'in_progress', 'done', 'cancelled']:
    return jsonify({'error': 'Status inválido'}), 400
if priority < 1 or priority > 5:
```
Description: Handlers de 40–90 linhas fazem validação, verificação de existência de FKs, parse de data, conversão de tags, cálculo de atraso/estatísticas e acesso direto a `Model.query`/`db.session`. Existem `services/` e `utils/helpers.process_task_data`, mas nenhum handler os usa (organização apenas aparente).
Impact: Regra de negócio não reutilizável nem testável isoladamente; cada endpoint reimplementa as mesmas regras.
Recommendation: Extrair regras para models/services e criar controllers finos; rotas apenas mapeiam URL → controller. Ver playbook AP-06.

### F-06 [HIGH] Acoplamento forte sem injeção de dependência
Catalog: AP-08
File:
- app.py:9-31
- services/notification_service.py:15
- seed.py:2
Evidence:
```python
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
server = smtplib.SMTP(self.email_host, self.email_port)
```
Description: Não há factory/composition root: o app é criado, configurado e tem `db.create_all()` executado no import do módulo; `seed.py` importa o app global. O serviço de notificação instancia o cliente SMTP dentro do método de negócio.
Impact: Impossível criar uma instância de app com outra configuração (ex.: banco de teste) ou substituir o SMTP por um fake.
Recommendation: `create_app(config)` como composition root; serviço externo recebido por construtor. Ver playbook AP-08.

### F-07 [HIGH] Exposição de dados sensíveis em respostas
Catalog: AP-09
File:
- models/user.py:21
- routes/user_routes.py:33
- routes/user_routes.py:85-86
- routes/user_routes.py:129
- routes/user_routes.py:209
Evidence:
```python
'email': self.email,
'password': self.password,
```
Description: `User.to_dict()` inclui o hash da senha, devolvido em `GET /users/<id>`, `POST /users`, `PUT /users/<id>` e `POST /login`.
Impact: Qualquer cliente obtém hashes MD5 de todos os usuários (combinado com F-02, recuperação trivial da senha).
Recommendation: Serializer sem campos sensíveis. Ver playbook AP-09.

### F-08 [MEDIUM] Queries N+1
Catalog: AP-10
File:
- routes/task_routes.py:41-51
- routes/user_routes.py:22
- routes/report_routes.py:55-56
- routes/report_routes.py:161-163
- routes/report_routes.py:19-28
- routes/task_routes.py:276-279
Evidence:
```python
for t in tasks:
    ...
        user = User.query.get(t.user_id)
        cat = Category.query.get(t.category_id)
```
Description: `GET /tasks` faz 2 queries por task; `GET /users` acessa `u.tasks` (lazy) por usuário; o resumo faz 1 query por usuário; `GET /categories` faz 1 `count()` por categoria; contagens por status/prioridade usam 9 queries em vez de `GROUP BY`.
Impact: Latência cresce linearmente com o volume de dados.
Recommendation: Eager loading (`selectinload`/`joinedload`) e agregação com `GROUP BY`. Ver playbook AP-10.

### F-09 [MEDIUM] Exclusão de registro pai sem tratar dependentes
Catalog: AP-11
File:
- routes/report_routes.py:211-223
Evidence:
```python
db.session.delete(cat)
db.session.commit()
```
Description: `DELETE /categories/<id>` remove a categoria sem tratar as tasks que a referenciam (sem cascade/`SET NULL`; SQLite não aplica FK por padrão).
Impact: Tasks ficam com `category_id` órfão apontando para registro inexistente.
Recommendation: Desassociar (`category_id = NULL`) as tasks na mesma transação antes de excluir. Ver playbook AP-11.

### F-10 [MEDIUM] Validação de entrada ausente, duplicada ou inconsistente
Catalog: AP-12
File:
- routes/task_routes.py:113
- routes/task_routes.py:167
- routes/task_routes.py:261
- routes/task_routes.py:264
- routes/report_routes.py:196-197
- routes/task_routes.py:96-114
- routes/user_routes.py:61-72
- requirements.txt:4
Evidence:
```python
data = request.get_json()
if 'name' in data:
```
Description: `priority` não-numérico gera `TypeError` (500); `title: null` no PUT gera `TypeError`; `?priority=abc` gera `ValueError` (500); `PUT /categories` não checa body nulo. Validação de task/user copiada entre create e update (com regras divergentes de `utils/helpers.process_task_data`, que nunca é usado); `marshmallow` declarado e não usado; `color` não validado embora exista `is_valid_color`.
Impact: Entradas inválidas viram 500 em vez de 400; regras divergem entre endpoints.
Recommendation: Validador único por entidade, aplicado em create/update. Ver playbook AP-12.

### F-11 [MEDIUM] Tratamento de erro genérico e não centralizado
Catalog: AP-13
File:
- routes/task_routes.py:62
- routes/task_routes.py:137
- routes/task_routes.py:151
- routes/task_routes.py:204
- routes/task_routes.py:221
- routes/task_routes.py:236
- routes/user_routes.py:87
- routes/user_routes.py:130
- routes/user_routes.py:149
- routes/report_routes.py:186
- routes/report_routes.py:207
- routes/report_routes.py:221
Evidence:
```python
    except:
        db.session.rollback()
        return jsonify({'error': 'Erro ao deletar'}), 500
```
Description: `except:` bare em todos os handlers de escrita, sem log; nenhum `@app.errorhandler` — 404/405/500 não tratados retornam HTML, divergindo do formato `{'error': ...}`.
Impact: Erros reais (inclusive `KeyboardInterrupt`/`SystemExit`) são engolidos; diagnóstico impossível; contrato de erro inconsistente.
Recommendation: Exceções de domínio + error handler central. Ver playbook AP-13.

### F-12 [MEDIUM] Uso de APIs deprecated
Catalog: AP-14
File:
- models/category.py:11
- models/user.py:14
- models/task.py:15-16
- models/task.py:52
- routes/task_routes.py:31, 72, 215, 285
- routes/user_routes.py:172
- routes/report_routes.py:35, 42, 45, 71, 133
- services/notification_service.py:35
- utils/helpers.py:38
- seed.py:66, 67, 69, 70, 74
- routes/task_routes.py:42, 51, 67, 117, 122, 158, 188, 195, 227
- routes/user_routes.py:29, 94, 136, 155
- routes/report_routes.py:105, 192, 213
Evidence:
```python
created_at = db.Column(db.DateTime, default=datetime.utcnow)
task = Task.query.get(task_id)
```
Description: `datetime.utcnow()` é deprecated desde Python 3.12 (runtime 3.14). `Query.get()` é legado no SQLAlchemy 2.x (exigido por Flask-SQLAlchemy 3.1.1) e emite `LegacyAPIWarning`.
Impact: Warnings em runtime; remoção em versões futuras.
Recommendation: `datetime.now(timezone.utc)` e `db.session.get(Model, id)`. Ver playbook AP-14.

### F-13 [MEDIUM] Lógica de negócio duplicada
Catalog: AP-16
File:
- models/task.py:50-60
- routes/task_routes.py:30-39
- routes/task_routes.py:71-80
- routes/task_routes.py:283-287
- routes/user_routes.py:171-180
- routes/report_routes.py:33-36
- routes/report_routes.py:132-135
- routes/task_routes.py:17-28
- routes/user_routes.py:15-22
Evidence:
```python
if t.due_date:
    if t.due_date < datetime.utcnow():
        if t.status != 'done' and t.status != 'cancelled':
```
Description: A regra de "task atrasada" existe em `Task.is_overdue()` mas é reimplementada 6 vezes nas rotas; `GET /tasks` reescreve manualmente `Task.to_dict()`; `GET /users` reescreve `User.to_dict()`; contagem por status repetida em `task_stats` e `summary_report`; conversão de tags duplicada (`task_routes.py:140-144`, `209-213`).
Impact: Alterar a regra exige editar vários lugares; risco de divergência.
Recommendation: Centralizar no model/service e reutilizar. Ver playbook AP-16.

### F-14 [LOW] Magic numbers e strings
Catalog: AP-17
File:
- routes/task_routes.py:110
- routes/task_routes.py:177
- models/task.py:39
- routes/user_routes.py:71
- routes/user_routes.py:120
- routes/task_routes.py:96-99
- routes/task_routes.py:167-169
- routes/user_routes.py:64
- routes/user_routes.py:115
- app.py:11
- app.py:34
- utils/helpers.py:110-116
Evidence:
```python
if status not in ['pending', 'in_progress', 'done', 'cancelled']:
if role not in ['user', 'admin', 'manager']:
```
Description: Listas de status/roles e limites (3, 200, 4, 1–5) repetidos como literais; as constantes `VALID_STATUSES`, `VALID_ROLES`, `MIN_TITLE_LENGTH` etc. existem em `utils/helpers.py` mas são ignoradas. URI do banco e porta fixas.
Impact: Alterar uma regra exige caçar literais espalhados.
Recommendation: Constantes únicas no domínio/config. Ver playbook AP-17.

### F-15 [LOW] `print` como mecanismo de logging
Catalog: AP-18
File:
- routes/task_routes.py:149
- routes/task_routes.py:153
- routes/task_routes.py:219
- routes/task_routes.py:234
- routes/user_routes.py:83
- routes/user_routes.py:89
- routes/user_routes.py:147
- services/notification_service.py:21
- services/notification_service.py:24
- utils/helpers.py:39
- utils/helpers.py:41
Evidence:
```python
print(f"Task criada: {task.id} - {task.title}")
print(f"ERRO: {str(e)}")
```
Description: Eventos e erros registrados com `print`, sem nível, sem timestamp padronizado.
Impact: Logs não filtráveis nem roteáveis em produção.
Recommendation: Módulo `logging`. Ver playbook AP-18.

### F-16 [LOW] Nomenclatura ruim
Catalog: AP-19
File:
- routes/report_routes.py:24-28
- models/category.py:14
- models/task.py:45
- models/user.py:27
Evidence:
```python
p1 = Task.query.filter_by(priority=1).count()
p2 = Task.query.filter_by(priority=2).count()
```
Description: Variáveis `p1..p5`, `d`, `p`, `pwd`, `u`, `t`, `c` sem significado fora de loops curtos.
Impact: Leitura e manutenção mais difíceis.
Recommendation: Nomes descritivos (sem alterar campos do contrato). Ver playbook AP-19.

### F-17 [LOW] Código morto e imports não utilizados
Catalog: AP-20
File:
- app.py:7
- routes/task_routes.py:7
- routes/user_routes.py:6
- routes/report_routes.py:7-8
- models/task.py:3
- utils/helpers.py:3-7
- utils/helpers.py:9-116
- utils/helpers.py:33
- services/notification_service.py:1-48
- requirements.txt:5
Evidence:
```python
import os, sys, json, datetime
import json, os, sys, time
from utils.helpers import format_date, calculate_percentage
```
Description: Imports nunca usados em quase todos os módulos; nenhuma função/constante de `utils/helpers.py` é chamada; `NotificationService` nunca é importado; `requests` declarado e nunca importado; import dentro de função (`uuid`).
Impact: Ruído, falsa impressão de camadas existentes, dependências desnecessárias.
Recommendation: Remover ou integrar o que for útil. Ver playbook AP-20.

### F-18 [LOW] Condicionais verbosas / aninhamento excessivo
Catalog: AP-21
File:
- models/task.py:38-48
- models/task.py:50-60
- models/user.py:34-38
- utils/helpers.py:21-23
- routes/task_routes.py:141
- routes/task_routes.py:210
- routes/report_routes.py:57-61
- routes/report_routes.py:119-135
Evidence:
```python
if self.role == 'admin':
    return True
else:
    return False
```
Description: `if cond: return True else: return False`; `if` aninhados em 3 níveis para atraso; `type(x) == list`; contadores manuais em loops onde cabe agregação.
Impact: Código mais longo e propenso a erro.
Recommendation: Retornar a expressão, guard clauses, `isinstance`, agregação no banco. Ver playbook AP-21.

## Deprecated APIs
| Location | Deprecated API | Modern replacement |
|---|---|---|
| `models/category.py:11`, `models/user.py:14`, `models/task.py:15-16` | `default=datetime.utcnow` | `default=lambda: datetime.now(timezone.utc)` |
| `models/task.py:52`, `routes/task_routes.py:31`, `routes/task_routes.py:72`, `routes/task_routes.py:215`, `routes/task_routes.py:285` | `datetime.utcnow()` (Python ≥ 3.12) | `datetime.now(timezone.utc)` |
| `routes/user_routes.py:172`, `routes/report_routes.py:35`, `routes/report_routes.py:42`, `routes/report_routes.py:45`, `routes/report_routes.py:71`, `routes/report_routes.py:133` | `datetime.utcnow()` (Python ≥ 3.12) | `datetime.now(timezone.utc)` |
| `services/notification_service.py:35`, `utils/helpers.py:38`, `seed.py:66`, `seed.py:67`, `seed.py:69`, `seed.py:70`, `seed.py:74` | `datetime.utcnow()` (Python ≥ 3.12) | `datetime.now(timezone.utc)` |
| `routes/task_routes.py:42`, `routes/task_routes.py:51`, `routes/task_routes.py:67`, `routes/task_routes.py:117`, `routes/task_routes.py:122`, `routes/task_routes.py:158`, `routes/task_routes.py:188`, `routes/task_routes.py:195`, `routes/task_routes.py:227` | `Model.query.get(id)` (SQLAlchemy 2.x legacy) | `db.session.get(Model, id)` |
| `routes/user_routes.py:29`, `routes/user_routes.py:94`, `routes/user_routes.py:136`, `routes/user_routes.py:155`, `routes/report_routes.py:105`, `routes/report_routes.py:192`, `routes/report_routes.py:213` | `Model.query.get(id)` (SQLAlchemy 2.x legacy) | `db.session.get(Model, id)` |

## Architecture Overview
Current:  Camadas parciais — models/routes/services/utils existem, mas rotas fazem tudo (ORM, regras, validação, serialização); services/utils mortos; sem factory, config ou error handler.
Target:   MVC — `config/` (env), `models/` (entidades + regras de domínio), `controllers/` (orquestração/validação), `routes/` (blueprints finos), `middlewares/` (error handler), `create_app()` como composition root.
Key moves:
- Criar `config/settings.py` + `create_app()`; segredos e debug via env; `.env.example`.
- Mover validação/regras das rotas para controllers e models (`is_overdue`, `to_dict` sem senha, validadores únicos); separar categorias de relatórios.
- Error handler central com exceções de domínio; `logging`; hashing pbkdf2; bloquear `role` no cadastro público.
- Remover código morto (helpers, notification service não usados, imports, deps `requests`/`marshmallow`).

================================
Total: 18 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
