================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~780 lines of code
Date:    2026-10-13

## Summary
CRITICAL: 6 | HIGH: 4 | MEDIUM: 5 | LOW: 4

| # | Severity | Anti-pattern | Location |
|---|---|---|---|
| F-01 | CRITICAL | SQL Injection (AP-01) | `models.py:109-111`, `models.py:289-299`, `app.py:59-78` +17 |
| F-02 | CRITICAL | Hardcoded credentials and secrets (AP-02) | `app.py:7`, `app.py:8`, `app.py:88` +1 |
| F-03 | CRITICAL | Insecure password storage (AP-03) | `models.py:126-129`, `models.py:109-111`, `database.py:75-83` |
| F-04 | CRITICAL | Sensitive endpoint without auth (AP-04) | `app.py:47-57`, `app.py:59-78`, `controllers.py:176-180` +2 |
| F-05 | CRITICAL | God File (AP-05) | `models.py:1-314`, `app.py:1-88`, `database.py:1-86` |
| F-06 | CRITICAL | Sensitive data exposure (AP-09) | `controllers.py:285-289`, `models.py:83`, `models.py:99` +17 |
| F-07 | HIGH | Fat Controller (AP-06) | `controllers.py:24-62`, `controllers.py:188-220`, `controllers.py:264-292` +4 |
| F-08 | HIGH | Mutable global state (AP-07) | `database.py:4`, `database.py:8-10` |
| F-09 | HIGH | Tight coupling without DI (AP-08) | `controllers.py:266`, `app.py:49`, `models.py:5` +16 |
| F-10 | HIGH | Multi-step operation without transaction (AP-11) | `models.py:133-169`, `models.py:65-70` |
| F-11 | MEDIUM | N+1 queries (AP-10) | `models.py:177-199`, `models.py:209-231`, `models.py:139-140` +2 |
| F-12 | MEDIUM | Missing/duplicated/inconsistent validation (AP-12) | `controllers.py:169-170`, `controllers.py:118-121`, `controllers.py:195-201` +3 |
| F-13 | MEDIUM | Generic, non-centralized error handling (AP-13) | `controllers.py:10-12`, `controllers.py:291-292`, `app.py:77-78` +15 |
| F-14 | MEDIUM | Duplicated business logic (AP-16) | `models.py:171-201`, `models.py:203-233`, `controllers.py:26-50` +5 |
| F-15 | MEDIUM | Magic numbers and strings (AP-17) | `models.py:256-262`, `controllers.py:52`, `controllers.py:242` +6 |
| F-16 | LOW | print as logging (AP-18) | `controllers.py:208-210`, `controllers.py:248-250`, `app.py:56` +9 |
| F-17 | LOW | Poor naming (AP-19) | `controllers.py:14`, `models.py:24`, `models.py:187-191` +7 |
| F-18 | LOW | Dead code and unused imports (AP-20) | `models.py:2`, `database.py:2`, `controllers.py:268` +3 |
| F-19 | LOW | Verbose conditionals (AP-21) | `controllers.py:200` |

## Findings

### F-01 [CRITICAL] SQL Injection
Catalog: AP-01
File:
- models.py:28
- models.py:47-50
- models.py:57-61
- models.py:68
- models.py:92
- models.py:109-111
- models.py:126-129
- models.py:140
- models.py:148-151
- models.py:155
- models.py:157-161
- models.py:163-166
- models.py:174
- models.py:188
- models.py:192
- models.py:220
- models.py:224
- models.py:279-281
- models.py:289-299
- app.py:59-78
Evidence:
```python
cursor.execute(
    "SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'"
)
```
Description: Todas as queries são montadas por concatenação. Strings vindas do body (`nome`, `descricao`, `categoria`, `email`, `senha`, `status`) e da query string (`q`, `categoria` em `/produtos/busca`, linhas 291/293) vão direto para o SQL. Além disso, `/admin/query` (`app.py:69`) executa SQL arbitrário enviado no payload.
Impact: Login sem senha com `' OR 1=1 --`; leitura de todas as tabelas via `UNION` na busca; alteração ou destruição de dados.
Recommendation: Queries parametrizadas (`?` + tupla) em todo o repositório; remover `/admin/query`. Ver playbook AP-01.

### F-02 [CRITICAL] Hardcoded credentials and secrets
Catalog: AP-02
File:
- app.py:7
- app.py:8
- app.py:88
- controllers.py:286-289
Evidence:
```python
app.config["SECRET_KEY"] = "minh***"
app.config["DEBUG"] = True
```
Description: `SECRET_KEY` está fixa no código e duplicada em `controllers.py:289`; o modo debug está forçado (`DEBUG = True`, `app.run(..., debug=True)`) e o health check declara `"ambiente": "producao"`.
Impact: Quem tem acesso ao código pode forjar sessões/assinaturas. O debugger do Werkzeug, ligado em `0.0.0.0`, permite execução remota de código.
Recommendation: Módulo `config` que lê variáveis de ambiente, `.env.example` e debug desligado por padrão. Ver playbook AP-02.

### F-03 [CRITICAL] Insecure password storage
Catalog: AP-03
File:
- models.py:126-129
- models.py:109-111
- database.py:75-83
Evidence:
```python
"INSERT INTO usuarios (nome, email, senha, tipo) VALUES ('" +
nome + "', '" + email + "', '" + senha + "', '" + tipo + "')"
```
Description: As senhas são gravadas em texto puro. O login compara a senha diretamente no SQL (`AND senha = '...'`) e o seed insere senhas em claro (`"admi***"`, `"1234***"`, `"senh***"`).
Impact: Um vazamento do `loja.db` (ou de `/usuarios`, ver F-06) expõe todas as credenciais, que podem ser reutilizadas em outros serviços.
Recommendation: Hash adaptativo com salt (`werkzeug.security.generate_password_hash` / `check_password_hash`), com verificação em Python e não no SQL; seed com hash. Ver playbook AP-03.

### F-04 [CRITICAL] Sensitive endpoint without authentication/authorization
Catalog: AP-04
File:
- app.py:47-57
- app.py:59-78
- controllers.py:176-180
- app.py:18-19
- app.py:28
Evidence:
```python
@app.route("/admin/reset-db", methods=["POST"])
def reset_database():
    ...
    cursor.execute("DELETE FROM usuarios")
```
Description: `/admin/reset-db` apaga todas as tabelas e `/admin/query` executa SQL arbitrário, os dois sem autenticação. O login não emite token, e nenhuma rota verifica identidade: `/usuarios` e `/relatorios/vendas` ficam públicos.
Impact: Qualquer cliente anônimo pode apagar o banco, ler ou alterar qualquer dado e listar todos os usuários.
Recommendation: Remover os endpoints `/admin/*` (no mínimo, protegê-los por autenticação e papel admin). Ver playbook AP-04.

### F-05 [CRITICAL] God File
Catalog: AP-05
File:
- models.py:1-314
- app.py:1-88
- database.py:1-86
Evidence:
```python
desconto = 0
if faturamento > 10000:
    desconto = faturamento * 0.1
```
Description: `models.py` mistura SQL, serialização e regras de negócio (cálculo de total, checagem de estoque, faixas de desconto nas linhas 256-262) para 4 domínios (produtos, usuários, pedidos, relatórios). `app.py` junta configuração (7-8), mapeamento de rotas (11-45) e rotas com SQL inline (47-78). `database.py` junta conexão, schema DDL e seed.
Impact: Qualquer mudança mexe em vários domínios ao mesmo tempo; é impossível testar regras sem banco; o acoplamento é alto.
Recommendation: Separar em `config/`, `models/` (um por entidade), `controllers/`, `routes/` (blueprints), `database` e seed. Ver playbook AP-05.

### F-06 [CRITICAL] Sensitive data exposure in responses and logs
Catalog: AP-09 (severidade elevada para CRITICAL: expõe o segredo da aplicação)
File:
- controllers.py:285-289
- models.py:83
- models.py:99
- controllers.py:12
- controllers.py:22
- controllers.py:62
- controllers.py:96
- controllers.py:109
- controllers.py:126
- controllers.py:134
- controllers.py:144
- controllers.py:165
- controllers.py:186
- controllers.py:220
- controllers.py:227
- controllers.py:235
- controllers.py:255
- controllers.py:262
- controllers.py:292
- app.py:78
Evidence:
```python
"db_path": "loja.db",
"debug": True,
"secret_key": "minh***"
```
Description: `/health` devolve a secret key, o flag de debug e o caminho do banco. `GET /usuarios` e `GET /usuarios/<id>` serializam o campo `senha`. Todos os handlers devolvem `str(e)` ao cliente, o que vaza detalhes internos (SQL, schema).
Impact: Qualquer cliente obtém a secret key e as senhas de todos os usuários; as mensagens de erro ajudam a explorar a SQL injection de F-01.
Recommendation: Serializer de usuário sem `senha`; health check só com status e contagens; mensagem de erro genérica com log interno. Ver playbook AP-09.

### F-07 [HIGH] Fat Controller
Catalog: AP-06
File:
- controllers.py:24-62
- controllers.py:64-96
- controllers.py:188-220
- controllers.py:237-255
- controllers.py:264-292
- app.py:47-57
- app.py:59-78
Evidence:
```python
print("ENVIANDO EMAIL: Pedido " + str(resultado["pedido_id"]) + " criado para usuario " + str(usuario_id))
print("ENVIANDO SMS: Seu pedido foi recebido!")
print("ENVIANDO PUSH: Novo pedido recebido pelo sistema")
```
Description: `criar_produto` tem 39 linhas de validação e regra (categorias válidas, limites). `criar_pedido` e `atualizar_status_pedido` disparam notificações (efeitos colaterais de negócio) no handler; o comentário de "Devolver estoque" nem é executado. `health_check` e as rotas `/admin/*` fazem SQL direto na camada de rota.
Impact: Regras de negócio espalhadas e não testáveis isoladamente; comportamento divergente entre rotas.
Recommendation: Extrair validação para schemas, regras e notificações para services/models; controller apenas orquestra. Ver playbook AP-06.

### F-08 [HIGH] Mutable global state
Catalog: AP-07
File:
- database.py:4
- database.py:8-10
Evidence:
```python
global db_connection
if db_connection is None:
    db_connection = sqlite3.connect(db_path, check_same_thread=False)
```
Description: Uma única conexão SQLite global e mutável é compartilhada entre todas as threads de requisição (`check_same_thread=False`).
Impact: Condições de corrida em requisições concorrentes; escritas não confirmadas de uma requisição que falhou são confirmadas pelo `commit()` de outra (ver F-10).
Recommendation: Conexão por requisição em `flask.g`, fechada no `teardown_appcontext`. Ver playbook AP-07.

### F-09 [HIGH] Tight coupling without dependency injection
Catalog: AP-08
File:
- controllers.py:3
- controllers.py:266
- app.py:4
- app.py:49
- app.py:66
- models.py:1
- models.py:5
- models.py:25
- models.py:44
- models.py:55
- models.py:66
- models.py:73
- models.py:90
- models.py:106
- models.py:123
- models.py:134
- models.py:172
- models.py:204
- models.py:236
- models.py:276
- models.py:286
Evidence:
```python
def health_check():
    try:
        db = get_db()
```
Description: Cada função chama `get_db()` direto do módulo concreto `database`; não existe composition root (`create_app`), e o caminho do banco é fixo.
Impact: Não é possível trocar o banco em testes (ex.: SQLite temporário) nem configurar instâncias diferentes da aplicação.
Recommendation: App factory `create_app(config)` como composition root; a conexão é obtida via app context configurado pela factory. Ver playbook AP-08.

### F-10 [HIGH] Multi-step operation without transaction
Catalog: AP-11 (HIGH: envolve estoque e valores)
File:
- models.py:133-169
- models.py:65-70
Evidence:
```python
cursor.execute(
    "UPDATE produtos SET estoque = estoque - " + str(item["quantidade"]) +
    " WHERE id = " + str(item["produto_id"])
)
```
Description: `criar_pedido` insere o pedido, os itens e decrementa o estoque com um único `commit()` no fim, sem `rollback()`. Uma falha no meio deixa as escritas pendentes na conexão global, e o próximo commit de qualquer requisição as confirma. A checagem de estoque (144) é separada do decremento (163-166), o que abre corrida. `deletar_produto` apaga o produto e deixa `itens_pedido` órfãos.
Impact: Pedidos sem itens, estoque inconsistente ou negativo, relatórios incorretos.
Recommendation: Transação explícita (`with conn:`) com rollback; validar tudo antes de escrever; decremento condicional ao estoque. Ver playbook AP-11.

### F-11 [MEDIUM] N+1 queries
Catalog: AP-10
File:
- models.py:177-199
- models.py:209-231
- models.py:139-140
- models.py:154-155
- models.py:247-254
Evidence:
```python
for item in itens:
    cursor3 = db.cursor()
    cursor3.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))
```
Description: A listagem de pedidos faz uma query de itens por pedido e uma query de produto por item. `criar_pedido` busca o mesmo produto duas vezes por item. O relatório faz uma query `COUNT` por status em vez de `GROUP BY`.
Impact: O número de queries cresce linearmente com pedidos e itens, e a latência degrada com o volume.
Recommendation: `JOIN itens_pedido/produtos` em uma query, agrupando em Python; `GROUP BY status` no relatório; reutilizar o produto já carregado. Ver playbook AP-10.

### F-12 [MEDIUM] Missing, duplicated or inconsistent input validation
Catalog: AP-12
File:
- controllers.py:169-170
- controllers.py:239-240
- controllers.py:118-121
- controllers.py:195-201
- controllers.py:26-54
- controllers.py:66-90
Evidence:
```python
dados = request.get_json()
email = dados.get("email", "")
senha = dados.get("senha", "")
```
Description: `login` e `atualizar_status_pedido` usam `dados.get` sem checar `None`, o que gera 500. `preco_min`/`preco_max` passam por `float()` sem tratamento. Os itens do pedido não são validados (`produto_id`/`quantidade` ausentes geram KeyError; uma quantidade negativa *aumenta* o estoque). A validação de produto é copiada entre create e update com regras divergentes: o update não valida categoria nem tamanho do nome. `preco`/`estoque` não têm checagem de tipo (uma string gera TypeError → 500).
Impact: Erros 500 com input malformado; corrupção de estoque; dados inválidos gravados via PUT.
Recommendation: Um validador único por entidade, aplicado em create e update, que retorna 400 com mensagem clara. Ver playbook AP-12.

### F-13 [MEDIUM] Generic, non-centralized error handling
Catalog: AP-13
File:
- controllers.py:10-12
- controllers.py:21-22
- controllers.py:60-62
- controllers.py:95-96
- controllers.py:108-109
- controllers.py:125-126
- controllers.py:133-134
- controllers.py:143-144
- controllers.py:164-165
- controllers.py:185-186
- controllers.py:218-220
- controllers.py:226-227
- controllers.py:234-235
- controllers.py:254-255
- controllers.py:261-262
- controllers.py:291-292
- app.py:77-78
Evidence:
```python
except Exception as e:
    return jsonify({"erro": str(e)}), 500
```
Description: Todos os handlers repetem `try/except Exception`. Não existe `@app.errorhandler`, e os formatos de erro são inconsistentes (`{"erro"}`, `{"erro","sucesso":false}`, `{"status":"erro","detalhes"}`).
Impact: Duplicação, vazamento de detalhes internos e erros que o cliente não consegue tratar de forma uniforme.
Recommendation: Exceções de domínio (`NotFound`, `ValidationError`) e um error handler central. Ver playbook AP-13.

### F-14 [MEDIUM] Duplicated business logic
Catalog: AP-16
File:
- models.py:171-201
- models.py:203-233
- models.py:12-21
- models.py:31-40
- models.py:304-313
- models.py:79-86
- models.py:95-102
- controllers.py:26-50
- controllers.py:66-90
Evidence:
```python
cursor2 = db.cursor()
cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))
itens = cursor2.fetchall()
```
Description: `get_pedidos_usuario` e `get_todos_pedidos` são idênticas, exceto pelo filtro. A serialização de produto aparece 3 vezes e a de usuário 2 vezes. A validação de produto está copiada entre create e update.
Impact: Correções aplicadas em um lugar e esquecidas no outro (a divergência de validação já existe, ver F-12).
Recommendation: Uma função de listagem de pedidos com filtro opcional; `to_dict` único por entidade; validador compartilhado. Ver playbook AP-16.

### F-15 [MEDIUM] Magic numbers and strings
Catalog: AP-17 (MEDIUM: a regra de desconto depende dos literais)
File:
- models.py:256-262
- controllers.py:52
- controllers.py:242
- controllers.py:47-50
- models.py:150
- models.py:247-253
- database.py:5
- controllers.py:287
- app.py:85-88
Evidence:
```python
if faturamento > 10000:
    desconto = faturamento * 0.1
elif faturamento > 5000:
```
Description: As faixas de desconto, a lista de categorias válidas, a lista de status de pedido, os limites de nome (2/200), os literais de status (`'pendente'`, `'aprovado'`, `'cancelado'`), o caminho `loja.db` (duplicado) e a porta 5000 estão espalhados como literais.
Impact: Mudar uma regra exige caçar literais; risco de divergência entre os pontos que usam o mesmo valor.
Recommendation: Constantes nomeadas em um módulo de domínio/config. Ver playbook AP-17.

### F-16 [LOW] print as logging mechanism
Catalog: AP-18
File:
- controllers.py:8
- controllers.py:11
- controllers.py:57
- controllers.py:61
- controllers.py:106
- controllers.py:161
- controllers.py:179
- controllers.py:182
- controllers.py:208-210
- controllers.py:219
- controllers.py:248-250
- app.py:56
- app.py:83-86
Evidence:
```python
print("Login bem-sucedido: " + email)
```
Description: Todo o logging usa `print`, sem níveis; notificações são simuladas com print. E-mails de usuário (PII) são logados em claro.
Impact: Sem controle de nível ou destino; logs poluídos e com dados pessoais.
Recommendation: Módulo `logging` com logger por módulo e níveis adequados. Ver playbook AP-18.

### F-17 [LOW] Poor naming
Catalog: AP-19
File:
- controllers.py:14
- controllers.py:56
- controllers.py:64
- controllers.py:98
- controllers.py:160
- models.py:24
- models.py:54
- models.py:65
- models.py:89
- models.py:187-191
- models.py:219-223
Evidence:
```python
def buscar_produto(id):
    try:
        produto = models.get_produto_por_id(id)
```
Description: O builtin `id` é sombreado em parâmetros e variáveis; cursores se chamam `cursor2`/`cursor3`; nomes genéricos como `result` e `prod`.
Impact: Legibilidade menor e risco de bugs por sombreamento.
Recommendation: Nomes descritivos (`produto_id`, `itens_cursor`). O contrato da API não muda. Ver playbook AP-19.

### F-18 [LOW] Dead code and unused imports
Catalog: AP-20
File:
- models.py:2
- database.py:2
- controllers.py:268
- models.py:63
- models.py:70
- models.py:283
Evidence:
```python
from database import get_db
import sqlite3
```
Description: `sqlite3` em models.py e `os` em database.py não são usados. `cursor.execute("SELECT 1")` no health tem o resultado descartado. `return True` em `atualizar_produto`, `deletar_produto` e `atualizar_status_pedido` nunca é lido.
Impact: Ruído e falsa impressão de dependências.
Recommendation: Remover. Ver playbook AP-20.

### F-19 [LOW] Verbose conditionals
Catalog: AP-21
File:
- controllers.py:200
Evidence:
```python
if not itens or len(itens) == 0:
```
Description: A condição é redundante: `not itens` já cobre a lista vazia.
Impact: Ruído de leitura.
Recommendation: `if not itens:`. Ver playbook AP-21.

## Deprecated APIs
| Location | Deprecated API | Modern replacement |
|---|---|---|
| — | None detected | — |

Verificado (Flask 3.1.1, sqlite3 stdlib): `before_first_request`, `json_encoder`/`JSONEncoder`, `_app_ctx_stack`/`_request_ctx_stack`, `datetime.utcnow`/`utcfromtimestamp`, `pkg_resources`, `distutils`/`imp`, `Model.query.get`/`declarative_base`. Nenhuma ocorrência.

## Architecture Overview
Current:  Monolito desestruturado: 4 arquivos planos com SQL concatenado, regras de negócio em models e controllers, rotas com SQL inline e config hardcoded.
Target:   MVC — `app.py` (composition root `create_app`) + `config/` + `database.py` (conexão por request + schema/seed) + `models/` (produto, usuario, pedido, relatorio) + `controllers/` + `routes/` (blueprints) + `middlewares/` (error handler)
Key moves:
- Mover config e segredos para variáveis de ambiente; criar app factory e trocar a conexão global por conexão por request
- Reescrever o acesso a dados com queries parametrizadas, transação no pedido, JOINs no lugar de N+1 e hash de senha
- Controllers finos com validadores por entidade, error handler central e logging; remover endpoints `/admin/*` e dados sensíveis das respostas

================================
Total: 19 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
