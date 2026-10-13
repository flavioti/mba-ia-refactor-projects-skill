# Catálogo de Anti-Patterns

Catálogo usado na **Fase 2 (Auditoria)**. Cada anti-pattern traz: severidade padrão, sinais de detecção por linguagem, casos que **não** são finding, a evidência a registrar e a recomendação (a transformação concreta está em `refactoring-playbook.md`, na seção com o mesmo ID).

## Escala de severidade

| Severidade | Critério |
|---|---|
| **CRITICAL** | Falha grave de segurança ou arquitetura: expõe dados sensíveis, permite comprometer o sistema ou viola completamente a separação de responsabilidades. |
| **HIGH** | Forte violação de MVC/SOLID que dificulta muito manutenção e testes: lógica de negócio em controllers/rotas, acoplamento forte sem DI, estado global mutável. |
| **MEDIUM** | Padronização, duplicação, performance moderada, robustez: N+1, validação ausente, falta de transação, APIs deprecated. |
| **LOW** | Legibilidade: nomes ruins, magic numbers, código morto, logging improvisado. |

## Como aplicar

1. Para cada anti-pattern, rode os padrões de busca sugeridos (Grep) **e** confirme lendo o código ao redor.
2. Os padrões são pontos de partida, não prova: sempre verifique contexto.
3. Registre **todas** as localizações; consolide ocorrências de mesma causa em um único finding.
4. Se a linguagem detectada não aparecer nos exemplos, aplique o **conceito** do sinal à sintaxe equivalente.

## Índice

| ID | Anti-pattern | Severidade | Categoria |
|---|---|---|---|
| AP-01 | SQL Injection | CRITICAL | Segurança |
| AP-02 | Credenciais e segredos hardcoded | CRITICAL | Segurança |
| AP-03 | Armazenamento inseguro de senhas | CRITICAL | Segurança |
| AP-04 | Endpoint sensível sem autenticação/autorização | CRITICAL | Segurança |
| AP-05 | God Class / God File | CRITICAL | Arquitetura |
| AP-06 | Fat Controller (regra de negócio na camada de rota) | HIGH | Arquitetura |
| AP-07 | Estado global mutável | HIGH | Arquitetura |
| AP-08 | Acoplamento forte sem injeção de dependência | HIGH | Arquitetura |
| AP-09 | Exposição de dados sensíveis em respostas e logs | HIGH | Segurança |
| AP-10 | Queries N+1 | MEDIUM | Performance |
| AP-11 | Operação multi-etapa sem transação | MEDIUM | Integridade |
| AP-12 | Validação de entrada ausente, duplicada ou inconsistente | MEDIUM | Robustez |
| AP-13 | Tratamento de erro genérico e não centralizado | MEDIUM | Robustez |
| AP-14 | Uso de APIs deprecated | MEDIUM | Manutenibilidade |
| AP-15 | Callback hell / fluxo assíncrono aninhado | MEDIUM | Legibilidade/Robustez |
| AP-16 | Lógica de negócio duplicada | MEDIUM | Manutenibilidade |
| AP-17 | Magic numbers e strings | LOW | Legibilidade |
| AP-18 | `print`/`console.log` como mecanismo de logging | LOW | Observabilidade |
| AP-19 | Nomenclatura ruim | LOW | Legibilidade |
| AP-20 | Código morto e imports não utilizados | LOW | Legibilidade |
| AP-21 | Condicionais verbosas / aninhamento excessivo | LOW | Legibilidade |

---

## CRITICAL

### AP-01 — SQL Injection
**Severidade:** CRITICAL

**Descrição:** query SQL construída concatenando ou interpolando valores que vêm (direta ou indiretamente) da requisição.

**Sinais de detecção:**
- Python: `"SELECT ... " + var`, `f"... WHERE x = {var}"`, `"... %s" % var`, `"...".format(var)` passados para `execute(`/`executescript(`.
- JavaScript/TypeScript: `` `SELECT ... ${var}` `` ou `"SELECT ..." + var` passados para `.query(`, `.run(`, `.get(`, `.all(`, `.exec(`.
- Qualquer linguagem: função de acesso a dados recebendo **uma única string** montada dinamicamente, sem lista/array de parâmetros.
- `LIKE '%" + termo + "%'` em buscas.
- Endpoint que recebe SQL bruto no payload e executa (também é AP-04).

**Grep sugerido:**
- `execute\(.*\+` · `execute\(f["']` · `(SELECT|INSERT|UPDATE|DELETE).*["']\s*\+` · `\$\{.*\}.*(WHERE|VALUES)` · `(WHERE|VALUES).*\$\{`

**Não é finding:**
- Placeholders com parâmetros separados: `execute("... WHERE id = ?", (id,))`, `db.get("... = ?", [id])`, `%s`/`:nome` com dict.
- ORM/query builder (`filter_by(...)`, `Model.where(...)`, `.like(f'%{q}%')` do SQLAlchemy — o ORM parametriza).
- Concatenação apenas de literais constantes do código (sem dado externo) — no máximo AP-17.

**Evidência:** cada linha que monta/executa a query + a origem do dado (parâmetro de rota, body, query string).

**Recomendação:** queries parametrizadas ou ORM. → Playbook AP-01.

---

### AP-02 — Credenciais e segredos hardcoded
**Severidade:** CRITICAL

**Descrição:** chaves, senhas, tokens ou configurações sensíveis escritas no código-fonte; modo debug ligado fixo.

**Sinais de detecção:**
- Atribuições com nomes como `SECRET`, `SECRET_KEY`, `PASSWORD`, `PASS`, `PWD`, `TOKEN`, `API_KEY`, `KEY`, `CREDENTIAL`, `smtp`, `dbPass` recebendo **literal string**.
- Strings com cara de chave: `pk_live_`, `sk_live_`, `AKIA`, `ghp_`, `-----BEGIN`.
- Connection strings com usuário/senha embutidos.
- `DEBUG = True`, `debug=True` em `app.run(...)`, `NODE_ENV` forçado para dev no código.
- Segredo retornado em resposta HTTP (ex.: health check devolvendo `secret_key`) — agrava; citar também em AP-09.
- Biblioteca de env (`python-dotenv`, `dotenv`) declarada mas nunca usada.

**Grep sugerido:**
- `(?i)(secret|password|passwd|pass|pwd|token|api_?key|credential)\w*["']?\s*[:=]\s*["'][^"']+["']` · `debug\s*=\s*True` · `pk_live|sk_live`

**Não é finding:**
- Leitura de ambiente: `os.environ[...]`, `os.getenv(...)`, `process.env.X`.
- Placeholders óbvios em `.env.example`/documentação.
- Dados de seed de usuários de teste → avaliar como AP-03 (senha em texto puro), não AP-02.

**Evidência:** arquivo:linha de cada segredo (pode mascarar o valor no relatório).

**Recomendação:** módulo de configuração lendo variáveis de ambiente; `.env.example`; debug controlado por env. → Playbook AP-02.

---

### AP-03 — Armazenamento inseguro de senhas
**Severidade:** CRITICAL

**Descrição:** senhas gravadas em texto puro, com hash rápido/quebrado ou com "criptografia" caseira.

**Sinais de detecção:**
- Coluna `senha`/`password`/`pass` recebendo o valor da requisição sem transformação.
- Comparação de login direto no SQL: `WHERE email = ? AND senha = ?`.
- `hashlib.md5`, `hashlib.sha1`, `sha256` sem salt/iterações, `crypto.createHash('md5'|'sha1')` aplicados a senha.
- Funções caseiras (`badCrypto`, base64, loops com substring, `reverse`) usadas como hash.
- Senha padrão fixa quando o usuário não envia (`p || "123456"`).
- Seeds com senhas em texto puro.

**Grep sugerido:**
- `md5|sha1|createHash|base64|btoa` · `(?i)(senha|password|pass)\s*=\s*` · `AND\s+(senha|password)\s*=`

**Não é finding:** `bcrypt`, `argon2`, `scrypt`, `pbkdf2` com salt, `werkzeug.security.generate_password_hash`.

**Evidência:** onde a senha é gravada, onde é verificada e o algoritmo usado.

**Recomendação:** hash adaptativo com salt (bcrypt/argon2/pbkdf2) e verificação em tempo constante. → Playbook AP-03.

---

### AP-04 — Endpoint sensível sem autenticação/autorização
**Severidade:** CRITICAL (HIGH se o endpoint só expõe dados de leitura não sensíveis)

**Descrição:** operações administrativas, destrutivas ou de privilégio acessíveis por qualquer cliente.

**Sinais de detecção:**
- Rotas com `admin`, `reset`, `query`, `exec`, `debug`, `report`, `financial` sem middleware/decorator de auth.
- Endpoint que executa SQL ou comando recebido no payload.
- Endpoint que apaga dados em massa (`DELETE FROM tabela` sem `WHERE`).
- Login que retorna token falso/previsível (`'fake-jwt-token-' + id`) ou nenhum token, e rotas que nunca verificam identidade.
- Cadastro que aceita `role`/`tipo`/`is_admin` do próprio payload (escalada de privilégio).

**Grep sugerido:** `admin|reset|/query|fake|token` · `role|tipo|is_admin` em handlers de criação de usuário.

**Não é finding:** rotas protegidas por decorator/middleware de auth efetivamente verificado (`@login_required`, `@jwt_required`, `authMiddleware`).

**Evidência:** definição da rota + ausência de verificação.

**Recomendação:** remover endpoints perigosos; exigir autenticação e checagem de papel; nunca aceitar papel do payload público. → Playbook AP-04.

---

### AP-05 — God Class / God File
**Severidade:** CRITICAL (HIGH se o arquivo concentra apenas 2 responsabilidades de um único domínio)

**Descrição:** um arquivo/classe concentra várias responsabilidades de camadas e domínios distintos (conexão, schema, seed, rotas, regra de negócio, serialização).

**Sinais de detecção:**
- Um arquivo contém **≥ 3** destes: SQL/ORM, definição de rotas, regra de negócio (cálculos, decisões), validação de entrada, formatação de resposta, configuração, seed de dados.
- Um arquivo de "models" com funções para **≥ 3 domínios/entidades** diferentes, misturando SQL e regra de negócio.
- Classe com nome genérico (`Manager`, `*Manager`, `Utils`, `Helper`, `Service` único) com métodos para conexão, rotas e negócio.
- Arquivo de aplicação que também define rotas com SQL inline.
- Tamanho é sinal auxiliar (> 300 linhas ou > 15 funções), nunca critério único.

**Não é finding:** arquivo grande mas coeso (ex.: um model com muitos campos de uma entidade só).

**Evidência:** intervalo de linhas do arquivo/classe + lista das responsabilidades encontradas.

**Recomendação:** separar por camada (model, controller, rota, config) e por domínio. → Playbook AP-05.

---

## HIGH

### AP-06 — Fat Controller (regra de negócio na camada de rota)
**Severidade:** HIGH

**Descrição:** handlers de rota/controllers que, além de orquestrar, contêm validação extensa, cálculos, regras de negócio e acesso direto ao banco.

**Sinais de detecção:**
- Handler com **> 30 linhas** ou com SQL/ORM direto (`Model.query`, `db.session`, `cursor.execute`, `db.run`) **e** regras (cálculos, mudanças de estado, decisões de negócio).
- Efeitos colaterais de negócio no handler: envio de email/SMS/notificação, cálculo de preço/desconto, decisão de aprovação de pagamento.
- Existe camada de service/helper no projeto, mas os handlers não a usam (organização apenas aparente).

**Não é finding:** handler fino que extrai dados da requisição, chama um service/model e formata a resposta.

**Evidência:** intervalo de linhas de cada handler afetado e o que ele contém que não deveria.

**Recomendação:** extrair regra para model/service; controller orquestra; rota só mapeia. → Playbook AP-06.

---

### AP-07 — Estado global mutável
**Severidade:** HIGH

**Descrição:** variáveis de módulo mutáveis compartilhadas entre requisições (conexões, caches, contadores, listas).

**Sinais de detecção:**
- Python: `global x` dentro de funções; variáveis de módulo (`db_connection = None`, `cache = {}`, `items = []`) reatribuídas/mutadas em funções.
- JS: `let x = {}`/`let total = 0` no escopo do módulo, mutados em handlers; objetos mutáveis exportados.
- Conexão única compartilhada entre threads (`check_same_thread=False`).
- Estado guardado em atributos de instância de serviços singleton (`self.notifications = []`).
- Exportar primitivo mutável (`module.exports = { total }`) — o importador recebe cópia, a atualização se perde.

**Grep sugerido:** `^\s*global\s` · `^(let|var)\s+\w+\s*=\s*(\{|\[|0)` · `check_same_thread`

**Não é finding:** constantes imutáveis (`MAX_X = 10`, tuplas, `Object.freeze`); objetos de framework criados uma vez e configurados (`app`, `db = SQLAlchemy()`).

**Evidência:** declaração + pontos de mutação.

**Recomendação:** injeção de dependência, escopo por requisição/app context, cache explícito com limites. → Playbook AP-07.

---

### AP-08 — Acoplamento forte sem injeção de dependência
**Severidade:** HIGH

**Descrição:** módulos instanciam ou importam diretamente suas dependências concretas (banco, serviços externos), impedindo substituição em testes.

**Sinais de detecção:**
- Controllers/handlers chamando `get_db()`/`new Database()`/`sqlite3.connect` diretamente.
- Classe criando o próprio banco no construtor (`this.db = new sqlite3.Database(...)`).
- Serviço externo (SMTP, gateway de pagamento) instanciado dentro da função de negócio.
- Entry point sem composition root: a montagem das dependências está espalhada.

**Não é finding:** composition root (entry point/factory `create_app`) instanciando e injetando dependências.

**Evidência:** pontos de instanciação/acesso direto.

**Recomendação:** composition root + injeção por parâmetro/construtor/factory. → Playbook AP-08.

---

### AP-09 — Exposição de dados sensíveis em respostas e logs
**Severidade:** HIGH (CRITICAL se expõe segredo da aplicação ou dado de cartão completo)

**Descrição:** senha/hash, segredos, dados de cartão ou detalhes internos de erro vazando para o cliente ou para logs.

**Sinais de detecção:**
- Serialização (`to_dict`, `toJSON`, dict manual) incluindo `password`/`senha`/`hash`.
- `SELECT *` de usuários retornado direto na resposta.
- Log com número de cartão, senha, token ou chave (`console.log(... ${card} ... ${key})`).
- `str(e)`/`err.message`/stack trace devolvidos ao cliente.
- Health check/endpoint de status retornando configuração interna (secret, debug, caminho do banco).

**Evidência:** linha da serialização/log/resposta.

**Recomendação:** DTO/serializer explícito sem campos sensíveis; mascarar logs; mensagem de erro genérica ao cliente com log interno. → Playbook AP-09.

---

## MEDIUM

### AP-10 — Queries N+1
**Severidade:** MEDIUM

**Descrição:** uma query por item de uma coleção já carregada.

**Sinais de detecção:**
- Query (`execute`, `.get(`, `.query`, `.all(`, `Model.query.get`, `filter_by(...).count()`) **dentro de** `for`/`forEach`/`map` sobre resultado de outra query.
- Acesso a relacionamento lazy dentro de loop (`len(u.tasks)`, `task.user.name`) sem eager loading.
- Contagens por categoria/status feitas com N queries em vez de `GROUP BY`.

**Não é finding:** loop sobre dados já carregados em memória; batch com `IN (...)`; `joinedload`/`selectinload`/`include`.

**Evidência:** linha do loop + linha da query interna.

**Recomendação:** `JOIN`, eager loading, `IN (...)`, agregação com `GROUP BY`. → Playbook AP-10.

---

### AP-11 — Operação multi-etapa sem transação
**Severidade:** MEDIUM (HIGH se envolve dinheiro/pagamento ou estoque)

**Descrição:** várias escritas dependentes (pedido + itens + estoque; matrícula + pagamento) sem atomicidade.

**Sinais de detecção:**
- Sequência de `INSERT`/`UPDATE` com `commit()` só no fim e sem `rollback()` em `except`.
- Escritas aninhadas em callbacks sem `BEGIN`/`COMMIT`/`ROLLBACK`.
- Retorno antecipado (validação) no meio de escritas já executadas.
- Exclusão de registro pai sem tratar filhos (registros órfãos), sem FK/cascade.

**Evidência:** intervalo de linhas da operação.

**Recomendação:** transação explícita (context manager / `BEGIN…COMMIT` / `session.begin()`), validar antes de escrever, cascade ou exclusão explícita de dependentes. → Playbook AP-11.

---

### AP-12 — Validação de entrada ausente, duplicada ou inconsistente
**Severidade:** MEDIUM

**Sinais de detecção:**
- Uso de campos do body sem checar presença/tipo (`dados.get("x")` usado em comparação numérica; `req.body.x.startsWith`).
- `request.get_json()` podendo ser `None` e usado com `in`/`.get` → 500.
- Mesmo bloco de validação copiado entre create/update, com regras divergentes.
- Biblioteca de validação declarada (`marshmallow`, `pydantic`, `joi`, `zod`) e não usada.
- Parâmetros de query convertidos sem tratamento (`int(request.args[...])`).

**Evidência:** blocos de validação (ou ausência) com linhas; divergências entre eles.

**Recomendação:** schema/validador único por entidade, aplicado em todas as operações. → Playbook AP-12.

---

### AP-13 — Tratamento de erro genérico e não centralizado
**Severidade:** MEDIUM

**Sinais de detecção:**
- Python: `except:` (bare) ou `except Exception as e: return ... str(e)` repetido em todo handler.
- JS: callbacks que ignoram `err` (`(err) => { res.send(...) }` sem checar `err`); falta de middleware `(err, req, res, next)`.
- Ausência de error handler central (`@app.errorhandler`, `app.use((err, req, res, next) => ...)`).
- Respostas de erro em formatos diferentes pela aplicação.

**Evidência:** linhas dos `try/except` genéricos ou erros ignorados.

**Recomendação:** exceções de domínio + handler central único. → Playbook AP-13.

---

### AP-14 — Uso de APIs deprecated
**Severidade:** MEDIUM (HIGH se a API já foi **removida** na versão declarada do framework/runtime)

**Descrição:** uso de APIs obsoletas que emitem warnings, foram removidas ou têm substituto moderno recomendado.

**Sinais de detecção** (verifique versões no manifesto):

| Stack | API deprecated | Equivalente moderno |
|---|---|---|
| Python ≥ 3.12 | `datetime.utcnow()`, `datetime.utcfromtimestamp()` | `datetime.now(timezone.utc)`, `datetime.fromtimestamp(ts, timezone.utc)` |
| Python ≥ 3.12 | `distutils`, `imp` (removidos) | `setuptools`/`packaging`, `importlib` |
| Python | `pkg_resources` | `importlib.metadata` / `importlib.resources` |
| SQLAlchemy ≥ 2.0 / Flask-SQLAlchemy ≥ 3 | `Model.query.get(id)` / `session.query(M).get(id)` | `db.session.get(Model, id)` |
| SQLAlchemy ≥ 2.0 | `Model.query.filter_by(...)` (estilo 1.x, legado) | `db.session.execute(db.select(Model).filter_by(...)).scalars()` |
| SQLAlchemy ≥ 2.0 | `from sqlalchemy.ext.declarative import declarative_base` | `from sqlalchemy.orm import DeclarativeBase` |
| Flask ≥ 2.3 | `@app.before_first_request` (removido) | inicialização na factory / `with app.app_context()` |
| Flask ≥ 2.3 | `app.json_encoder`, `flask.json.JSONEncoder` | `app.json` provider (`DefaultJSONProvider`) |
| Flask ≥ 2.2 | `flask._app_ctx_stack`, `_request_ctx_stack` | `flask.g`, `flask.current_app` |
| Node.js | `new Buffer(x)` | `Buffer.from(x)` / `Buffer.alloc(n)` |
| Node.js | `url.parse()` | `new URL()` |
| Node.js | `crypto.createCipher()` | `crypto.createCipheriv()` |
| Node.js | `fs.exists()` | `fs.existsSync()` / `fs.promises.access()` |
| Node.js | `util.isArray()` e afins | `Array.isArray()` |
| Express 4 | pacote `body-parser` separado | `express.json()` / `express.urlencoded()` |
| Express 4→5 | `req.param()`, `res.send(status, body)`, `res.json(status, obj)`, `res.sendfile()`, `app.del()` | `req.params/req.query/req.body`, `res.status(s).send()`, `res.sendFile()`, `app.delete()` |
| JS geral | callbacks aninhados de API que oferece Promise | `async/await` (ver também AP-15) |

**Grep sugerido:** `utcnow|utcfromtimestamp|\.query\.get\(|declarative_base|before_first_request|new Buffer\(|url\.parse|createCipher\(|body-parser|res\.sendfile|req\.param\(`

**Evidência:** cada chamada com arquivo:linha + versão declarada que torna a API obsoleta.

**Recomendação:** substituir pelo equivalente moderno da tabela. → Playbook AP-14.

---

### AP-15 — Callback hell / fluxo assíncrono aninhado
**Severidade:** MEDIUM

**Sinais de detecção:**
- **≥ 3 níveis** de callbacks aninhados (`db.get(..., (err, x) => { db.run(..., function(err) { ... }) })`).
- Contadores manuais de pendência para saber quando responder (`pending--; if (pending === 0) res.json(...)`).
- `const self = this` para acessar contexto em callbacks.
- Mistura de `function` e arrow functions para manipular `this` (`this.lastID`).

**Não é finding:** `async/await`, `Promise.all`, cadeias de `.then()` rasas.

**Evidência:** intervalo de linhas da pirâmide.

**Recomendação:** promisificar a API e usar `async/await` + `Promise.all`. → Playbook AP-15.

---

### AP-16 — Lógica de negócio duplicada
**Severidade:** MEDIUM

**Sinais de detecção:**
- Mesmo bloco de lógica (≥ 5 linhas ou mesma regra) em **≥ 2 lugares** — ex.: cálculo de "atrasado", serialização manual igual ao `to_dict()`, montagem do mesmo objeto de resposta.
- Método no model que resolve a regra (`is_overdue()`, `to_dict()`) existe mas é reimplementado nas rotas.
- Funções quase idênticas que diferem só por um filtro (`get_all_orders` vs `get_orders_by_customer`).

**Evidência:** todas as localizações duplicadas.

**Recomendação:** centralizar no model/service e reutilizar. → Playbook AP-16.

---

## LOW

### AP-17 — Magic numbers e strings
**Severidade:** LOW (MEDIUM se a regra de negócio — preço, desconto, aprovação — depende do literal)

**Sinais de detecção:**
- Números/strings literais com significado de negócio: faixas de desconto (`10000`, `0.1`), limites (`len(x) < 3`, `> 200`), status (`'pending'`, `"PAID"`), listas de valores válidos repetidas, portas, caminhos de banco.
- Regra codificada por literal (`cc.startsWith("4")` para aprovar pagamento).
- Constantes declaradas no projeto mas ignoradas em favor de literais.

**Não é finding:** `0`, `1`, `-1`, `100` em percentuais óbvios, códigos HTTP padrão.

**Recomendação:** constantes nomeadas/enum/config em um único lugar. → Playbook AP-17.

---

### AP-18 — `print`/`console.log` como mecanismo de logging
**Severidade:** LOW (escalar para AP-09 se loga dado sensível)

**Sinais de detecção:** `print(` em código de aplicação (fora de scripts CLI/seed); `console.log(` em handlers; logs simulando efeitos ("ENVIANDO EMAIL").

**Recomendação:** logger da linguagem (`logging`, `pino`/`winston` ou `console` encapsulado) com níveis. → Playbook AP-18.

---

### AP-19 — Nomenclatura ruim
**Severidade:** LOW

**Sinais de detecção:**
- Variáveis de 1–3 letras fora de loops curtos (`u`, `e`, `p`, `cc`, `cid`).
- Campos de API abreviados (`usr`, `eml`, `pwd`, `c_id`).
- Nomes genéricos (`data`, `result`, `manager`, `utils`, `doStuff`), nomes enganosos (`badCrypto`).
- Shadowing de builtins (`id`, `type`, `list`, `input`).
- Idiomas misturados de forma inconsistente no mesmo módulo.

**Recomendação:** nomes descritivos. Não renomeie campos do contrato da API (payload/resposta) sem listar como mudança de contrato. → Playbook AP-19.

---

### AP-20 — Código morto e imports não utilizados
**Severidade:** LOW

**Sinais de detecção:** imports nunca referenciados; funções/helpers/constantes nunca chamados; variáveis atribuídas e não lidas; imports dentro de funções sem motivo.

**Recomendação:** remover. → Playbook AP-20.

---

### AP-21 — Condicionais verbosas / aninhamento excessivo
**Severidade:** LOW

**Sinais de detecção:**
- `if cond: return True else: return False`.
- `if` aninhados **≥ 3 níveis** que podem ser combinados com `and`/guard clauses.
- Contadores incrementados manualmente em loop onde caberia `sum`/`filter`/`count` ou agregação no banco.
- `type(x) == list` em vez de `isinstance`.

**Recomendação:** retornar a expressão booleana, guard clauses, early return. → Playbook AP-21.
