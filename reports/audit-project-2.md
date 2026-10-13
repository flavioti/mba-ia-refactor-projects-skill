================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript (Node.js) + Express ^4.18.2
Files:   3 analyzed | ~180 lines of code
Date:    2026-10-13

## Summary
CRITICAL: 5 | HIGH: 4 | MEDIUM: 5 | LOW: 3

| # | Severity | Anti-pattern | Location |
|---|---|---|---|
| F-01 | CRITICAL | Credenciais e segredos hardcoded (AP-02) | `src/utils.js:2-5` |
| F-02 | CRITICAL | Armazenamento inseguro de senhas (AP-03) | `src/utils.js:17-23`, `src/AppManager.js:68`, `src/AppManager.js:18` |
| F-03 | CRITICAL | Endpoint sensível sem autenticação/autorização (AP-04) | `src/AppManager.js:80`, `src/AppManager.js:131` |
| F-04 | CRITICAL | God Class / God File (AP-05) | `src/AppManager.js:4-139` |
| F-05 | CRITICAL | Exposição de dados sensíveis em logs (AP-09) | `src/AppManager.js:45` |
| F-06 | HIGH | Fat Controller (AP-06) | `src/AppManager.js:28-78`, `src/AppManager.js:80-129` |
| F-07 | HIGH | Estado global mutável (AP-07) | `src/utils.js:9-10`, `src/utils.js:14`, `src/utils.js:25` |
| F-08 | HIGH | Acoplamento forte sem injeção de dependência (AP-08) | `src/AppManager.js:7`, `src/app.js:8-10` |
| F-09 | HIGH | Operação multi-etapa sem transação (AP-11) | `src/AppManager.js:50-60`, `src/AppManager.js:69`, `src/AppManager.js:133` |
| F-10 | MEDIUM | Queries N+1 (AP-10) | `src/AppManager.js:89-92`, `src/AppManager.js:102-106` |
| F-11 | MEDIUM | Validação de entrada ausente (AP-12) | `src/AppManager.js:35`, `src/AppManager.js:46`, `src/AppManager.js:132` |
| F-12 | MEDIUM | Tratamento de erro genérico e não centralizado (AP-13) | `src/AppManager.js:38`, `src/AppManager.js:57`, `src/AppManager.js:92` +3 |
| F-13 | MEDIUM | Callback hell / fluxo assíncrono aninhado (AP-15) | `src/AppManager.js:37-78`, `src/AppManager.js:83-128`, `src/AppManager.js:26` |
| F-14 | MEDIUM | Magic numbers e strings (AP-17) | `src/AppManager.js:46`, `src/AppManager.js:108`, `src/utils.js:6` |
| F-15 | LOW | `console.log` como mecanismo de logging (AP-18) | `src/utils.js:13`, `src/app.js:13` |
| F-16 | LOW | Nomenclatura ruim (AP-19) | `src/AppManager.js:29-33`, `src/utils.js:17`, `src/AppManager.js:4` |
| F-17 | LOW | Código morto e imports não utilizados (AP-20) | `src/AppManager.js:2`, `src/utils.js:2-5`, `src/utils.js:10` |

## Findings

### F-01 [CRITICAL] Credenciais e segredos hardcoded
Catalog: AP-02
File:
- src/utils.js:2
- src/utils.js:3
- src/utils.js:4
- src/utils.js:5
Evidence:
```javascript
    dbUser: "admi***",
    dbPass: "senh***", 
    paymentGatewayKey: "pk_l***",
```
Description: O usuário e a senha do banco, uma chave **live** do gateway de pagamento e o usuário SMTP estão escritos direto no código-fonte, no objeto `config`. Nada é lido de variáveis de ambiente.
Impact: Qualquer pessoa com acesso ao repositório tem as credenciais de produção. Trocar uma chave exige deploy de código, e o mesmo segredo vale para todos os ambientes.
Recommendation: Criar um módulo `config/` que lê de `process.env`, documentar as variáveis em `.env.example` e não usar fallback para segredos. Ver playbook AP-02.

### F-02 [CRITICAL] Armazenamento inseguro de senhas
Catalog: AP-03
File:
- src/utils.js:17-23
- src/AppManager.js:68
- src/AppManager.js:18
Evidence:
```javascript
        hash += Buffer.from(pwd).toString('base64').substring(0, 2);
...
                        let hash = badCrypto(p || "123456");
```
Description: O `badCrypto` repete os 2 primeiros caracteres do base64 da senha e corta em 10 caracteres. Isso não é hash: é reversível e gera colisões em massa (senhas com o mesmo prefixo dão o mesmo "hash"). Quando a senha não vem, o código usa a senha fixa `"123456"`. O seed grava a senha `'123'` em texto puro.
Impact: Se o banco vazar, todas as senhas ficam expostas na hora. Contas criadas sem senha ficam com uma senha conhecida.
Recommendation: Usar um hash adaptativo com salt (`crypto.scrypt` nativo, com comparação por `timingSafeEqual`), tornar `pwd` obrigatório e fazer hash da senha do seed. Ver playbook AP-03.

### F-03 [CRITICAL] Endpoint sensível sem autenticação/autorização
Catalog: AP-04
File:
- src/AppManager.js:80
- src/AppManager.js:131-136
Evidence:
```javascript
        app.get('/api/admin/financial-report', (req, res) => {
...
        app.delete('/api/users/:id', (req, res) => {
```
Description: O relatório financeiro administrativo (receita, nomes dos alunos, valores pagos) e a exclusão de usuários aceitam qualquer cliente anônimo. Não há middleware de autenticação nem checagem de papel.
Impact: Vazamento de dados financeiros e pessoais. Qualquer pessoa consegue apagar qualquer usuário enumerando IDs.
Recommendation: Criar um middleware de autorização administrativa (ex.: token de admin vindo do ambiente, enviado no header) e aplicá-lo às duas rotas. Ver playbook AP-04.

### F-04 [CRITICAL] God Class / God File
Catalog: AP-05
File:
- src/AppManager.js:4-139
Evidence:
```javascript
class AppManager {
    constructor() {
        this.db = new sqlite3.Database(':memory:');
```
Description: Uma única classe com nome genérico concentra a conexão com o banco (l.7), o schema e o seed (l.10-23), a definição de todas as rotas (l.25-138), validação (l.35), a regra de aprovação de pagamento (l.46), a criação de usuário com hash (l.68), o cálculo de receita (l.108-110) e a formatação das respostas.
Impact: Nenhuma parte pode ser testada ou reaproveitada sozinha. Qualquer mudança mexe no arquivo inteiro e os domínios (usuário, curso, matrícula, pagamento) ficam acoplados.
Recommendation: Separar em `config/`, `database/`, `models/` por entidade, `services/`, `controllers/`, `routes/` e `middlewares/`. Ver playbook AP-05.

### F-05 [CRITICAL] Exposição de dados sensíveis em logs
Catalog: AP-09
File:
- src/AppManager.js:45
Evidence:
```javascript
                        console.log(`Processando cartão ${cc} na chave ${config.paymentGatewayKey}`);
```
Description: A cada checkout, o número completo do cartão e a chave do gateway de pagamento vão para o log. Severidade elevada para CRITICAL pela regra do próprio AP-09 (dado de cartão completo + segredo da aplicação).
Impact: Os logs passam a guardar PAN e chave de produção, o que viola o PCI-DSS. Quem lê os logs (agregadores, terceiros) obtém os dois.
Recommendation: Nunca logar a chave. Mascarar o cartão (só os últimos 4 dígitos) e usar um logger com níveis. Ver playbook AP-09.

### F-06 [HIGH] Fat Controller (regra de negócio na camada de rota)
Catalog: AP-06
File:
- src/AppManager.js:28-78
- src/AppManager.js:80-129
Evidence:
```javascript
                        let status = cc.startsWith("4") ? "PAID" : "DENIED";
...
                                        courseData.revenue += payment.amount;
```
Description: O handler de checkout (51 linhas) valida, faz SQL direto, cria usuário com hash, decide a aprovação do pagamento, grava matrícula, pagamento e auditoria, e ainda escreve no cache. O handler do relatório (50 linhas) faz SQL e calcula a receita.
Impact: A regra de negócio não pode ser testada sem HTTP e sem banco, e não dá para reaproveitar o fluxo de checkout.
Recommendation: Extrair `CheckoutService` e `ReportService`. Os controllers ficam só com extrair a entrada, chamar o service e responder. Ver playbook AP-06.

### F-07 [HIGH] Estado global mutável
Catalog: AP-07
File:
- src/utils.js:9
- src/utils.js:10
- src/utils.js:14
- src/utils.js:25
Evidence:
```javascript
let globalCache = {};
let totalRevenue = 0;
...
    globalCache[key] = data;
```
Description: `globalCache` é um objeto de módulo mutado a cada checkout (por `logAndCache`, chamado em `AppManager.js:59`). Ele cresce sem limite e nunca é lido. `totalRevenue` é um primitivo mutável exportado: quem importa recebe uma cópia.
Impact: Vazamento de memória proporcional ao número de usuários, estado compartilhado entre requisições e um contador que, se fosse usado, nunca refletiria as atualizações.
Recommendation: Remover o cache inútil (ninguém o lê) e o contador. Se for preciso cache, usar um componente injetado e com limite. Ver playbook AP-07.

### F-08 [HIGH] Acoplamento forte sem injeção de dependência
Catalog: AP-08
File:
- src/AppManager.js:7
- src/app.js:8-10
Evidence:
```javascript
        this.db = new sqlite3.Database(':memory:');
```
Description: A classe cria o próprio banco no construtor. O entry point só chama `new AppManager()` e não monta as dependências (não há composition root). O gateway de pagamento é uma regra inline, sem abstração.
Impact: Não dá para trocar o banco (ex.: por um de teste) nem simular o gateway de pagamento em testes.
Recommendation: Entry point como composition root: criar a conexão, instanciar os models, o gateway e os services, e injetá-los por construtor. Ver playbook AP-08.

### F-09 [HIGH] Operação multi-etapa sem transação
Catalog: AP-11
File:
- src/AppManager.js:50-60
- src/AppManager.js:69
- src/AppManager.js:133
Evidence:
```javascript
                        this.db.run("INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)", [userId, cid], function(err) {
...
                            self.db.run("INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)", [enrId, course.price, status], function(err) {
```
Description: Matrícula, pagamento e auditoria são gravados em escritas separadas, sem `BEGIN/COMMIT/ROLLBACK`. O usuário é inserido (l.69) **antes** da decisão de pagamento, então um pagamento recusado deixa um usuário criado. O `DELETE` de usuário (l.133) não trata matrículas e pagamentos (a própria resposta admite: "ficaram sujos no banco"). Severidade HIGH porque envolve pagamento.
Impact: Matrículas sem pagamento ou pagamentos sem auditoria quando há falha parcial, além de registros órfãos.
Recommendation: Decidir o pagamento antes de qualquer escrita, envolver as escritas do checkout numa transação e excluir os dependentes do usuário na mesma transação. Ver playbook AP-11.

### F-10 [MEDIUM] Queries N+1
Catalog: AP-10
File:
- src/AppManager.js:89-92
- src/AppManager.js:102-106
Evidence:
```javascript
                        enrollments.forEach(enr => {
                            this.db.get("SELECT name, email FROM users WHERE id = ?", [enr.user_id], (err, user) => {
                                this.db.get("SELECT amount, status FROM payments WHERE enrollment_id = ?", [enr.id], (err, payment) => {
```
Description: O relatório faz 1 query de cursos, mais 1 query de matrículas por curso, mais 2 queries (usuário e pagamento) por matrícula.
Impact: O número de queries cresce linearmente com cursos e matrículas (1 + C + 2E) e o relatório fica lento com volume real.
Recommendation: Uma única query com `LEFT JOIN` entre courses, enrollments, users e payments, agregada em memória. Ver playbook AP-10.

### F-11 [MEDIUM] Validação de entrada ausente
Catalog: AP-12
File:
- src/AppManager.js:35
- src/AppManager.js:46
- src/AppManager.js:132
Evidence:
```javascript
            if (!u || !e || !cid || !cc) return res.status(400).send("Bad Request");
...
                        let status = cc.startsWith("4") ? "PAID" : "DENIED";
```
Description: A validação só checa se os campos existem. Não confere tipos (`card` numérico faz `cc.startsWith` lançar `TypeError` dentro de um callback do sqlite, o que **derruba o processo**), não valida email nem `c_id`, e `pwd` é opcional. O `:id` do DELETE não é validado.
Impact: Um único request malformado derruba a API inteira (DoS) e dados inválidos chegam ao banco.
Recommendation: Um validador único para o checkout (tipos e formatos) e validação do `id`, com 400 consistente. Ver playbook AP-12.

### F-12 [MEDIUM] Tratamento de erro genérico e não centralizado
Catalog: AP-13
File:
- src/AppManager.js:38
- src/AppManager.js:57
- src/AppManager.js:92-93
- src/AppManager.js:104
- src/AppManager.js:106
- src/AppManager.js:133-135
Evidence:
```javascript
                if (err || !course) return res.status(404).send("Curso não encontrado");
...
            this.db.run("DELETE FROM users WHERE id = ?", [id], (err) => {
```
Description: Erro de banco vira 404 (l.38). O `err` é ignorado nos callbacks das l.57, 92, 104, 106 e 133. Na l.92-93, um erro faz `enrollments.length` lançar exceção e derrubar o processo. Não existe middleware de erro `(err, req, res, next)`, e cada handler monta o próprio texto de erro.
Impact: Falhas silenciosas, respostas enganosas e crash do servidor em erro de banco.
Recommendation: Erros de domínio (`NotFoundError`, `ValidationError`, `PaymentDeclinedError`) e um middleware central que gera a resposta e registra o erro. Ver playbook AP-13.

### F-13 [MEDIUM] Callback hell / fluxo assíncrono aninhado
Catalog: AP-15
File:
- src/AppManager.js:37-78
- src/AppManager.js:83-128
- src/AppManager.js:26
Evidence:
```javascript
                                    enrPending--;
                                    if (enrPending === 0) {
                                        report.push(courseData);
```
Description: O checkout tem 5 níveis de callbacks aninhados. O relatório usa contadores manuais de pendência (`coursesPending`, `enrPending`, l.86, 93, 97, 117, 120), com o bloco de finalização duplicado (l.95-99 e l.118-122). Há `const self = this` e mistura de `function`/arrow para usar `this.lastID`.
Impact: Fluxo difícil de seguir e propenso a respostas duplicadas ou a nunca responder. A ordem do relatório não é determinística.
Recommendation: Promisificar o acesso ao sqlite (`run/get/all` → Promise) e usar `async/await`. Ver playbook AP-15.

### F-14 [MEDIUM] Magic numbers e strings
Catalog: AP-17
File:
- src/AppManager.js:46
- src/AppManager.js:48
- src/AppManager.js:108
- src/utils.js:6
Evidence:
```javascript
                        let status = cc.startsWith("4") ? "PAID" : "DENIED";
```
Description: A aprovação do pagamento depende do literal `"4"`. Os status `"PAID"`/`"DENIED"` se repetem como strings soltas e a porta `3000` é fixa. Severidade MEDIUM porque a regra de aprovação de pagamento depende de um literal.
Impact: Mudar a regra ou o status exige caçar strings pelo código, e um erro de digitação passa despercebido.
Recommendation: Constantes `PaymentStatus` e regra de aprovação encapsulada no gateway de pagamento. Porta via config/env. Ver playbook AP-17.

### F-15 [LOW] `console.log` como mecanismo de logging
Catalog: AP-18
File:
- src/utils.js:13
- src/app.js:13
Evidence:
```javascript
    console.log(`[LOG] Salvando no cache: ${key}`);
```
Description: Logging improvisado com `console.log` e prefixo manual, sem níveis. O log de `AppManager.js:45` foi escalado para F-05.
Impact: Não dá para filtrar por nível nem silenciar em testes ou produção.
Recommendation: Um logger único (wrapper de `console` com níveis) injetado ou importado de `utils/logger`. Ver playbook AP-18.

### F-16 [LOW] Nomenclatura ruim
Catalog: AP-19
File:
- src/AppManager.js:29-33
- src/AppManager.js:4
- src/utils.js:17
Evidence:
```javascript
            let u = req.body.usr;
            let e = req.body.eml;
            let p = req.body.pwd;
```
Description: Variáveis de 1-3 letras (`u`, `e`, `p`, `cid`, `cc`), nomes genéricos (`AppManager`, `utils`) e um nome enganoso (`badCrypto`). Os campos do payload (`usr`, `eml`, `pwd`, `c_id`, `card`) também são abreviados, mas fazem parte do contrato da API.
Impact: Leitura e manutenção mais difíceis.
Recommendation: Nomes descritivos internamente (`userName`, `email`, `password`, `courseId`, `cardNumber`). **Manter** os campos do payload para preservar o contrato. Ver playbook AP-19.

### F-17 [LOW] Código morto e imports não utilizados
Catalog: AP-20
File:
- src/AppManager.js:2
- src/utils.js:2
- src/utils.js:3
- src/utils.js:5
- src/utils.js:10
Evidence:
```javascript
const { config, logAndCache, badCrypto, totalRevenue } = require('./utils');
```
Description: `totalRevenue` é importado e nunca usado. `dbUser`, `dbPass` e `smtpUser` não são referenciados em nenhum lugar (o banco é `:memory:` e não há SMTP). `globalCache` é exportado e nunca lido.
Impact: Ruído que sugere funcionalidades inexistentes.
Recommendation: Remover. Ver playbook AP-20.

## Deprecated APIs
| Location | Deprecated API | Modern replacement |
|---|---|---|
| — | None detected | — |

Verificado: `new Buffer(` (o código usa `Buffer.from`, que está correto), `url.parse`, `crypto.createCipher`, `fs.exists`, `util.isArray`, `body-parser` (o código usa `express.json()`, que está correto), `req.param(`, `res.send(status, body)`, `res.sendfile`, `app.del(`. O estilo de callback aninhado está coberto em F-13.

## Architecture Overview
Current:  Monolito desestruturado: uma God Class (`AppManager`) com banco, seed, rotas e regras, mais um `utils` com segredos e estado global.
Target:   MVC: `config/` (env), `database/` (conexão promisificada + schema/seed), `models/` (repositórios por entidade), `services/` (checkout, relatório, gateway de pagamento, senha), `controllers/`, `routes/`, `middlewares/` (auth admin, erros), `app.js` como composition root.
Key moves:
- Desmontar `AppManager` em models/services/controllers/routes, com dependências injetadas a partir de `app.js`.
- Segredos para `process.env` com `.env.example`; hash `scrypt`; middleware de auth admin; logs mascarados.
- `async/await` sobre o sqlite promisificado, transações no checkout e na exclusão, relatório com um único `JOIN`, e error handler central.

================================
Total: 17 findings
================================

Nada foi alterado no projeto até aqui. Uma observação: o `node` não está no PATH deste shell. Antes de rodar o baseline da Fase 3 eu preciso localizar um runtime Node (ou você me diz onde ele está).

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
