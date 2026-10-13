# Criação de Skills — Refatoração Arquitetural Automatizada

Ao longo do curso você aprendeu o que são Skills e como elas permitem que um agente de IA atue como um especialista em tarefas específicas. Agora imagine o seguinte cenário: você herdou 3 projetos legados com problemas de arquitetura, segurança e qualidade de código. Revisar e corrigir tudo manualmente levaria dias.

Neste desafio, você vai criar uma Skill que automatiza esse processo — analisando, auditando e refatorando qualquer projeto para o padrão MVC, independente da tecnologia.

## Objetivo

Você deve entregar uma Skill capaz de:

- Analisar uma codebase detectando linguagem, framework e arquitetura atual
- Identificar anti-patterns e code smells, classificando por severidade com arquivo e linha exatos
- Gerar um relatório de auditoria estruturado com todos os achados
- Refatorar o projeto para o padrão MVC (Model-View-Controller), eliminando os problemas encontrados
- Validar o resultado garantindo que a aplicação continua funcionando após as mudanças

A skill deve ser agnóstica de tecnologia, funcionando com diferentes linguagens e frameworks.

## Contexto

### Definição de Severidades

Para padronizar a sua auditoria e os relatórios gerados pela IA, utilize a seguinte escala de classificação baseada em problemas de MVC e SOLID:

- **CRITICAL:** Falhas graves de arquitetura ou segurança que impedem o funcionamento correto, expõem dados sensíveis (ex: credenciais hardcoded, SQL Injection) ou violam completamente a separação de responsabilidades (ex: "God Class" contendo banco de dados, lógicas complexas e roteamento no mesmo arquivo).
- **HIGH:** Fortes violações do padrão MVC ou princípios SOLID que dificultam muito a manutenção e testes (ex: lógicas de negócio pesadas presas dentro de Controllers, forte acoplamento sem Injeção de Dependência, ou uso de estado global mutável em toda a aplicação).
- **MEDIUM:** Problemas de padronização, duplicação de código ou gargalos de performance moderada (ex: Queries N+1 no banco de dados, uso inadequado de middlewares, validações ausentes nas rotas).
- **LOW:** Melhorias de legibilidade, nomenclatura de variáveis ruins, ou "magic numbers" soltos pelo código.

### Exemplo de Uso no CLI

```bash
# Executar a skill no projeto com problemas
cd code-smells-project
claude "/refactor-arch"
```

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:      Flask 3.1.1
Dependencies:  flask-cors
Domain:        E-commerce API (produtos, pedidos, usuários)
Architecture:  Monolítica — tudo em 4 arquivos, sem separação de camadas
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~800 lines of code

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 2 | LOW: 3

## Findings

### [CRITICAL] God Class / God Method
File: models.py:1-350
Description: Arquivo único contém toda lógica de negócio, queries SQL, validação e formatação para 4 domínios diferentes.
Impact: Impossível testar em isolamento, qualquer mudança afeta tudo.
Recommendation: Separar em models e controllers por domínio.

### [CRITICAL] Hardcoded Credentials
File: app.py:8
Description: SECRET_KEY hardcoded como 'minha-chave-super-secreta-123'
...

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
```

```
[... refatoração executada ...]

================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
src/
├── config/settings.py
├── models/
│   ├── produto_model.py
│   └── usuario_model.py
├── views/
│   └── routes.py
├── controllers/
│   ├── produto_controller.py
│   └── pedido_controller.py
├── middlewares/error_handler.py
└── app.py (composition root)

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

## Tecnologias obrigatórias

- **Ferramenta:** uma das três opções abaixo (não são aceitas outras ferramentas):
  - Claude Code
  - Gemini CLI
  - OpenAI Codex
- **Recurso:** Custom Skills (ou o equivalente na ferramenta escolhida)
- **Formato dos arquivos de referência:** Markdown
- **Projetos-alvo:** Python/Flask (2 projetos) e Node.js/Express (1 projeto) (fornecidos no repositório base)

> **Nota sobre a ferramenta:** Os exemplos deste documento usam o Claude Code (`.claude/skills/`) como referência, pois é a ferramenta utilizada no curso. Se você optar por Gemini CLI ou Codex, adapte o nome da pasta e o comando de invocação conforme a convenção dela — o conceito de skill e a estrutura interna (SKILL.md + arquivos de referência) permanecem os mesmos.

## Requisitos

### 1. Análise Manual dos Projetos

Antes de criar a skill, você deve entender os problemas que ela vai resolver.

**Tarefas:**

- Analisar o projeto `code-smells-project/` (Python/Flask — API de E-commerce)
- Analisar o projeto `ecommerce-api-legacy/` (Node.js/Express — LMS API com fluxo de checkout)
- Analisar o projeto `task-manager-api/` (Python/Flask — API de Task Manager)

Para cada projeto, identificar e documentar no mínimo 5 problemas, incluindo pelo menos:

- 1 de severidade CRITICAL ou HIGH
- 2 de severidade MEDIUM
- 2 de severidade LOW

Documentar os achados na seção "Análise Manual" do seu `README.md`

> **Dica:** Não precisa encontrar todos os problemas — foque nos que têm maior impacto arquitetural. Use os projetos como insumo para entender quais padrões sua skill precisa detectar.

> **Por que 3 projetos?** Dois são Python/Flask (com níveis de organização diferentes) e um é Node.js/Express. Sua skill precisa funcionar nos 3 para provar que é verdadeiramente agnóstica de tecnologia — lidando tanto com código completamente desestruturado quanto com projetos que já possuem alguma separação de camadas.

### 2. Criação da Skill

Agora que você conhece os problemas, crie uma skill que os detecte, gere um relatório de auditoria e corrija automaticamente.

**Tarefas:**

Criar a skill dentro do projeto `code-smells-project/` e implementar o SKILL.md com 3 fases sequenciais:

- **Fase 1 — Análise:** Detectar stack, mapear arquitetura atual, imprimir resumo
- **Fase 2 — Auditoria:** Cruzar código contra catálogo de anti-patterns, gerar relatório, pedir confirmação
- **Fase 3 — Refatoração:** Reestruturar para o padrão MVC, validar que funciona

Criar arquivos de referência em Markdown que forneçam à skill o conhecimento necessário para executar as 3 fases. Os arquivos devem cobrir **obrigatoriamente** as seguintes áreas de conhecimento:

| Área de conhecimento | O que deve conter |
|---|---|
| Análise de projeto | Heurísticas para detecção de linguagem, framework, banco de dados e mapeamento de arquitetura |
| Catálogo de anti-patterns | Anti-patterns com sinais de detecção e classificação de severidade |
| Template de relatório | Formato padronizado do relatório de auditoria (Fase 2) |
| Guidelines de arquitetura | Regras do padrão MVC alvo (camadas Models, Views/Routes e Controllers, responsabilidades de cada uma) |
| Playbook de refatoração | Padrões concretos de transformação para cada anti-pattern (com exemplos de código) |

> **Nota:** Você tem liberdade para organizar os arquivos de referência como preferir — pode usar os nomes e a quantidade de arquivos que fizer sentido para sua skill. O importante é que todas as 5 áreas de conhecimento estejam cobertas. O nome da skill (`refactor-arch`) e o arquivo `SKILL.md` são obrigatórios e não devem ser alterados. O path da skill segue a convenção da ferramenta escolhida (no Claude Code, por exemplo, é `.claude/skills/refactor-arch/`).

**Requisitos da skill:**

- Deve ser agnóstica de tecnologia — deve funcionar corretamente nos 3 projetos fornecidos, independente da stack ou nível de organização
- O catálogo de anti-patterns deve conter no mínimo 8 anti-patterns com severidade distribuída (CRITICAL, HIGH, MEDIUM, LOW)
- O catálogo deve incluir detecção de APIs deprecated — identificar uso de APIs obsoletas e recomendar o equivalente moderno
- O playbook deve ter no mínimo 8 padrões de transformação com exemplos de código antes/depois
- A Fase 2 deve pausar e pedir confirmação antes de modificar qualquer arquivo
- A Fase 3 deve validar o resultado (boot da aplicação + endpoints funcionando)

### 3. Execução da Skill

Execute sua skill nos 3 projetos e valide que ela funciona em todas as stacks.

#### Projeto 1 — code-smells-project (Python/Flask)

Invocar a skill no Claude Code:

```bash
claude "/refactor-arch"
```

> **Nota:** O comando acima é o exemplo com Claude Code. Se você estiver usando Gemini CLI ou Codex, utilize o comando equivalente para invocar uma skill na sua ferramenta.

- Verificar que a Fase 1 detecta corretamente a stack e imprime o resumo
- Verificar que a Fase 2 encontra no mínimo 5 dos problemas documentados na sua análise manual
- Confirmar a execução da Fase 3
- Verificar que a Fase 3:
  - Cria a estrutura de diretórios baseada em MVC
  - A aplicação inicia sem erros
  - Os endpoints originais continuam respondendo
- Salvar o relatório de auditoria (output da Fase 2) em `reports/audit-project-1.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

Prove que sua skill é reutilizável em outro projeto de backend, mas com stack diferente.

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `ecommerce-api-legacy/`
- Invocar a skill:

```bash
cd ../ecommerce-api-legacy
claude "/refactor-arch"
```

- Verificar que as 3 fases executam corretamente neste projeto
- Salvar o relatório em `reports/audit-project-2.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 3 — task-manager-api (Python/Flask)

Agora o teste com um projeto Python/Flask que já possui alguma organização de camadas (models, routes, services, utils).

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `task-manager-api/`
- Invocar a skill:

```bash
cd ../task-manager-api
claude "/refactor-arch"
```

- Verificar que:
  - A Fase 1 detecta corretamente Python/Flask como stack e identifica o domínio de Task Manager
  - A Fase 2 identifica problemas mesmo em um projeto parcialmente organizado
  - A Fase 3 melhora a estrutura sem quebrar a aplicação (todos os endpoints devem continuar respondendo)
- Salvar o relatório em `reports/audit-project-3.md`
- Commitar o código refatorado do projeto no repositório

> **Nota:** Este projeto já possui alguma separação de camadas, mas isso não significa que a arquitetura está adequada. A skill deve identificar tanto problemas de código (segurança, performance, qualidade) quanto oportunidades de melhoria arquitetural. Se houver mudanças estruturais necessárias, a skill deve propô-las e executá-las.

#### Validação

Para cada projeto refatorado, valide o seguinte checklist:

```markdown
## Checklist de Validação

### Fase 1 — Análise
- [ ] Linguagem detectada corretamente
- [ ] Framework detectado corretamente
- [ ] Domínio da aplicação descrito corretamente
- [ ] Número de arquivos analisados condiz com a realidade

### Fase 2 — Auditoria
- [ ] Relatório segue o template definido nos arquivos de referência
- [ ] Cada finding tem arquivo e linhas exatos
- [ ] Findings ordenados por severidade (CRITICAL → LOW)
- [ ] Mínimo de 5 findings identificados
- [ ] Detecção de APIs deprecated incluída (se aplicável)
- [ ] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [ ] Estrutura de diretórios segue padrão MVC
- [ ] Configuração extraída para módulo de config (sem hardcoded)
- [ ] Models criados para abstrair dados
- [ ] Views/Routes separadas para visualização ou roteamento
- [ ] Controllers concentram o fluxo da aplicação
- [ ] Error handling centralizado
- [ ] Entry point claro
- [ ] Aplicação inicia sem erros
- [ ] Endpoints originais respondem corretamente
```

> **Dica:** Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Entregável

Repositório público no GitHub (fork do repositório base) contendo:

- Skill completa em `.claude/skills/refactor-arch/` (dentro dos 3 projetos)
- Código refatorado dos 3 projetos (resultado da execução da Fase 3, commitado no repositório)
- Relatórios de auditoria em `reports/` (3 arquivos)
- `README.md` atualizado

### Estrutura do repositório

Faça um fork do repositório base contendo os três projetos com code smells.

> **Nota:** A estrutura abaixo usa Claude Code como exemplo (`.claude/skills/`). Se estiver usando outra ferramenta, adapte os caminhos conforme a convenção dela.

```
desafio-skills/
├── README.md                              # Sua documentação
│
├── code-smells-project/                   # Projeto 1 — Python/Flask (API de E-commerce)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← SUA SKILL AQUI
│   │           ├── SKILL.md
│   │           └── (arquivos de referência)
│   ├── app.py
│   ├── controllers.py
│   ├── models.py
│   ├── database.py
│   └── requirements.txt
│
├── ecommerce-api-legacy/                  # Projeto 2 — Node.js/Express (LMS API com checkout)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── src/
│   │   ├── app.js
│   │   ├── AppManager.js
│   │   └── utils.js
│   ├── api.http
│   └── package.json
│
├── task-manager-api/                      # Projeto 3 — Python/Flask (API de Task Manager)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── app.py
│   ├── database.py
│   ├── seed.py
│   ├── requirements.txt
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
│
└── reports/                               # Relatórios gerados
    ├── audit-project-1.md                 # Saída da Fase 2 no projeto 1
    ├── audit-project-2.md                 # Saída da Fase 2 no projeto 2
    └── audit-project-3.md                 # Saída da Fase 2 no projeto 3
```

**O que você vai criar:**

- `.claude/skills/refactor-arch/` — A skill completa (SKILL.md + arquivos de referência)
- Código refatorado dos 3 projetos — resultado da execução da Fase 3, commitado no repositório
- `reports/audit-project-{1,2,3}.md` — Relatório de auditoria de cada projeto
- `README.md` — Documentação do seu processo

**O que já vem pronto:**

- `code-smells-project/` — API de E-commerce Python/Flask com code smells intencionais
- `ecommerce-api-legacy/` — LMS API Node.js/Express (com fluxo de checkout) e problemas de implementação
- `task-manager-api/` — API de Task Manager Python/Flask com organização parcial e problemas de segurança/qualidade

> **Dica:** Cada projeto contém problemas intencionais de diferentes severidades (CRITICAL, HIGH, MEDIUM, LOW), incluindo falhas de segurança, violações arquiteturais e problemas de qualidade de código. Parte do desafio é identificá-los por conta própria através da análise manual do código.

### README.md deve conter

**A) Seção "Análise Manual":**

- Lista dos problemas identificados manualmente em cada projeto
- Classificação por severidade
- Justificativa de por que cada problema é relevante

**B) Seção "Construção da Skill":**

- Decisões de design: como estruturou o SKILL.md e os arquivos de referência
- Quais anti-patterns incluiu no catálogo e por quê
- Como garantiu que a skill é agnóstica de tecnologia
- Desafios encontrados e como resolveu

**C) Seção "Resultados":**

- Resumo dos relatórios de auditoria dos 3 projetos (quantos findings por severidade em cada)
- Comparação antes/depois da estrutura de cada projeto
- Checklist de validação preenchido para cada projeto
- Screenshots ou logs mostrando as aplicações rodando após refatoração
- Observações sobre como a skill se comportou em stacks diferentes

**D) Seção "Como Executar":**

- Pré-requisitos (a ferramenta escolhida — Claude Code, Gemini CLI ou Codex — instalada e configurada)
- Comandos para executar a skill em cada projeto
- Como validar que a refatoração funcionou

### Ordem de execução sugerida

**1. Analisar os projetos manualmente**

Leia o código dos três projetos e documente os problemas encontrados.

**2. Criar a skill**

Escreva o SKILL.md e os arquivos de referência.

**3. Executar nos 3 projetos**

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

Salve a saída da Fase 2 de cada projeto em `reports/audit-project-{1,2,3}.md`.

**4. Iterar**

Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Critérios de Aceite

A skill deve atingir os seguintes mínimos em **todos os 3 projetos**:

| Critério | Requisito |
|---|---|
| Fase 1 detecta stack corretamente | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 encontra >= 5 findings | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 inclui pelo menos 1 CRITICAL ou HIGH | OBRIGATÓRIO (3/3 projetos) |
| Fase 3 aplicação funciona após refatoração | OBRIGATÓRIO (3/3 projetos) |

**IMPORTANTE:** Todos os critérios devem ser atingidos nos 3 projetos, não apenas em um!

> **Sobre o projeto 3 (task-manager-api):** Este projeto já possui alguma organização. "aplicação funciona" significa que a API inicia sem erros e todos os endpoints continuam respondendo corretamente.

## Referências

- [Claude Code: Skills](https://docs.anthropic.com/en/docs/claude-code/skills) — Documentação oficial sobre como criar e estruturar Skills
- [Claude Code: Overview](https://docs.anthropic.com/en/docs/claude-code/overview) — Visão geral do Claude Code e suas capacidades
- [The Complete Guide to Building Skills for Claude (PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) — Guia completo da Anthropic sobre construção de Skills
- [Equipping Agents for the Real World with Agent Skills](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills) — Blog oficial da Anthropic sobre Agent Skills

---

## Dicas Finais

- **Comece pela análise manual** — entender os problemas profundamente é essencial para criar uma skill que os detecte.
- **O SKILL.md é um prompt** — ele instrui o agente sobre o que fazer, enquanto os arquivos de referência fornecem o conhecimento de domínio.
- **Seja específico nos sinais de detecção** — "código ruim" não ajuda; "query SQL dentro de loop for" é acionável.
- **Teste incrementalmente** — não tente criar a skill perfeita de primeira.
- **A skill deve ser copiável** — se ela só funciona em um projeto específico, está acoplada demais. Teste nos 3 projetos para validar.
- **Projetos diferentes exigem adaptação** — a Fase 3 de um projeto já parcialmente organizado não vai ter as mesmas transformações de um monolito. Sua skill deve se adaptar ao contexto.
- **Pedir confirmação na Fase 2 é obrigatório** — o humano deve revisar o relatório antes de qualquer modificação.
- **Consulte as referências do curso** — revise a documentação oficial da ferramenta escolhida e os materiais das aulas para relembrar a estrutura e anatomia de uma skill.
---

## Análise Manual

Análise feita lendo o código dos três projetos antes de construir a skill. As severidades seguem a escala definida em [Definição de Severidades](#definição-de-severidades). Cada achado indica arquivo e linhas exatas, além da justificativa de por que o problema é relevante.

### Projeto 1 — code-smells-project (Python/Flask · API de E-commerce)

**Visão geral:** 4 arquivos (~780 linhas), sem separação real de camadas. O `models.py` mistura SQL cru, regra de negócio e serialização de 4 domínios (produtos, usuários, pedidos e relatórios). Os controllers falam direto com o banco e a configuração fica hardcoded no `app.py`.

| # | Severidade | Problema | Local | Por que é relevante |
|---|---|---|---|---|
| 1 | **CRITICAL** | SQL Injection: queries montadas por concatenação de strings com dados do usuário | `models.py:28`, `models.py:47-50`, `models.py:57-61`, `models.py:109-111`, `models.py:126-129`, `models.py:279-281`, `models.py:289-297` | No login, o email `' OR 1=1 --` autentica sem senha. Na busca (`?q=`), dá para ler ou apagar qualquer tabela. A correção é usar queries parametrizadas (`?`), que o próprio seed já usa em `database.py:70-73`. |
| 2 | **CRITICAL** | Credenciais hardcoded e vazadas: `SECRET_KEY` e `DEBUG=True` no código; o `/health` devolve a secret na resposta | `app.py:7-8`, `app.py:88`, `controllers.py:285-289` | A chave de sessão fica versionada no git e exposta publicamente num endpoint sem autenticação. O modo debug em produção permite executar código pelo debugger do Werkzeug. |
| 3 | **CRITICAL** | Endpoints administrativos sem autenticação: `/admin/query` executa qualquer SQL recebido e `/admin/reset-db` apaga todas as tabelas | `app.py:47-57`, `app.py:59-78` | Qualquer cliente HTTP consegue ler ou destruir o banco inteiro. É uma porta de administração aberta. |
| 4 | **HIGH** | Senhas em texto puro, retornadas no `GET /usuarios` e no `GET /usuarios/<id>` | `database.py:75-79`, `models.py:83`, `models.py:99`, `models.py:126-129` | Um vazamento do banco ou da API expõe as senhas reais dos usuários. Elas deveriam ser hasheadas (bcrypt/argon2) e nunca serializadas. |
| 5 | **HIGH** | Estado global mutável: conexão SQLite única compartilhada entre threads (`check_same_thread=False`) | `database.py:4-12` | Causa condições de corrida entre requisições, impede injeção de dependência e deixa os testes acoplados a um singleton. |
| 6 | **MEDIUM** | Queries N+1 na listagem de pedidos (1 + P + P·I consultas), com duas funções quase idênticas | `models.py:171-201`, `models.py:203-233` | O tempo de resposta cresce linearmente com o volume de dados, e qualquer correção precisa ser feita em dois lugares. Um único `JOIN` resolve. |
| 7 | **MEDIUM** | Validação duplicada e inconsistente: `atualizar_produto` não valida tamanho do nome nem categoria, e nenhum dos dois valida tipos (`preco` como string resulta em erro 500) | `controllers.py:24-54`, `controllers.py:64-90` | As regras de negócio já divergiram entre criação e atualização. Pelo PUT é possível gravar dados inválidos. |
| 8 | **MEDIUM** | `criar_pedido` sem transação: valida estoque, insere pedido, itens e baixa de estoque sem rollback em caso de falha | `models.py:133-169` | Uma falha no meio da operação deixa pedido sem itens ou estoque inconsistente. Além disso, a regra de negócio fica dentro da camada de dados. |
| 9 | **LOW** | Magic numbers: faixas de desconto (`10000`/`0.1`, `5000`/`0.05`, `1000`/`0.02`), tamanhos de nome, categorias e status como literais | `models.py:256-262`, `controllers.py:47-52`, `controllers.py:242` | A regra de desconto não tem nome nem fica centralizada, então mudá-la exige caçar literais pelo código. |
| 10 | **LOW** | `print()` usado como logging, incluindo emails de login (inclusive falhos) e notificações simuladas dentro do controller | `controllers.py:8`, `controllers.py:57`, `controllers.py:161`, `controllers.py:179-182`, `controllers.py:208-210`, `controllers.py:248-250` | Os logs não têm nível nem formato e não dá para filtrá-los. Dados pessoais vazam no stdout, e efeitos colaterais (email/SMS) ficam acoplados ao controller. |

### Projeto 2 — ecommerce-api-legacy (Node.js/Express · LMS API com checkout)

**Visão geral:** 3 arquivos (~180 linhas). A classe `AppManager` é uma "God Class" que cria o banco, faz o seed, registra rotas, processa pagamento e gera relatórios. O `utils.js` concentra segredos e estado global.

| # | Severidade | Problema | Local | Por que é relevante |
|---|---|---|---|---|
| 1 | **CRITICAL** | Credenciais hardcoded: senha do banco e chave **live** do gateway de pagamento no código; a chave e o número do cartão são impressos no log | `utils.js:1-7`, `AppManager.js:45` | Segredos de produção ficam versionados no git. Logar o número completo do cartão viola o PCI-DSS e expõe dados financeiros. |
| 2 | **CRITICAL** | Criptografia caseira e insegura: `badCrypto` repete os 2 primeiros caracteres do base64 da senha e trunca em 10; a senha padrão é `"123456"` quando não informada | `utils.js:17-23`, `AppManager.js:68` | O "hash" é reversível e colide trivialmente (senhas com o mesmo prefixo geram o mesmo valor). Usuários criados sem senha ficam com uma senha previsível. |
| 3 | **HIGH** | God Class: `AppManager` concentra conexão, schema, seed, roteamento, regra de pagamento, matrícula, auditoria e relatório | `AppManager.js:4-139` | Nenhuma parte pode ser testada ou reutilizada isoladamente, e é uma violação total de SRP e MVC. |
| 4 | **HIGH** | Estado global mutável: `globalCache` e `totalRevenue` exportados por módulo (`totalRevenue` é importado mas nunca usado) | `utils.js:9-10`, `utils.js:25`, `AppManager.js:2` | O cache cresce sem limite e é compartilhado entre requisições. Exportar um primitivo (`totalRevenue`) cria uma cópia, então qualquer "atualização" seria silenciosamente perdida. |
| 5 | **MEDIUM** | Checkout sem transação e em *callback hell*: matrícula, pagamento e auditoria em `INSERT`s aninhados sem rollback, e o erro do audit log é ignorado | `AppManager.js:28-78`, `AppManager.js:57-60` | Uma falha no pagamento deixa a matrícula criada sem pagamento. A pirâmide de callbacks dificulta a leitura e o tratamento de erros (async/await resolveria). |
| 6 | **MEDIUM** | Queries N+1 no relatório financeiro: para cada curso busca as matrículas, e para cada matrícula busca usuário e pagamento | `AppManager.js:80-129` | São 1 + C + 2·M consultas, com contadores manuais de pendência propensos a bugs (resposta dupla ou nunca enviada se `enrollments` vier `undefined` por erro). |
| 7 | **MEDIUM** | Rotas sem validação nem autorização: `/api/admin/financial-report` é público; `DELETE /api/users/:id` não verifica existência, ignora erro e deixa matrículas e pagamentos órfãos | `AppManager.js:80`, `AppManager.js:131-137` | Dados financeiros ficam expostos a qualquer cliente, e a integridade referencial é quebrada (a própria mensagem de resposta admite isso). |
| 8 | **LOW** | Nomenclatura críptica: variáveis `u`, `e`, `p`, `cid`, `cc` e campos de payload `usr`, `eml`, `pwd`, `c_id` | `AppManager.js:29-33` | O código fica difícil de ler e o contrato da API é obscuro para quem consome. |
| 9 | **LOW** | Magic values: aprovação de pagamento por `cc.startsWith("4")`, porta `3000`, banco `':memory:'`, loop `10000` | `AppManager.js:46`, `AppManager.js:7`, `utils.js:6`, `utils.js:19` | Regras e parâmetros de ambiente ficam escondidos em literais em vez de estar em config ou constantes nomeadas. O banco em memória perde todos os dados a cada restart. |

### Projeto 3 — task-manager-api (Python/Flask · API de Task Manager)

**Visão geral:** já existe separação parcial (`models/`, `routes/`, `services/`, `utils/`) com SQLAlchemy, mas as rotas são *fat controllers* com regra de negócio e acesso ao ORM. Os helpers e constantes que existem em `utils/` não são usados, e há problemas sérios de segurança.

| # | Severidade | Problema | Local | Por que é relevante |
|---|---|---|---|---|
| 1 | **CRITICAL** | Hash de senha com MD5 sem salt, e o hash é serializado em `to_dict()` e devolvido em `GET /users/<id>`, `POST /users`, `PUT /users/<id>` e `/login` | `models/user.py:16-25`, `models/user.py:27-32`, `routes/user_routes.py:33`, `routes/user_routes.py:85`, `routes/user_routes.py:209` | MD5 é quebrável por rainbow tables em segundos, e a API entrega o hash para qualquer cliente. O correto seria bcrypt/argon2 (`werkzeug.security`) e nunca expor o campo. |
| 2 | **CRITICAL** | Credenciais hardcoded: `SECRET_KEY` e usuário/senha SMTP no código; `debug=True` no entry point | `app.py:13`, `app.py:34`, `services/notification_service.py:7-10` | Segredos ficam versionados no git, e o debug ativo permite execução remota pelo console do Werkzeug. `python-dotenv` está no `requirements.txt` mas não é usado. |
| 3 | **HIGH** | Autenticação/autorização inexistente: o login retorna `fake-jwt-token-<id>`, nenhuma rota é protegida e `POST /users` aceita `role: "admin"` do próprio payload | `routes/user_routes.py:52`, `routes/user_routes.py:71-72`, `routes/user_routes.py:210` | Qualquer pessoa pode se cadastrar como admin, e o token é previsível e nunca verificado. |
| 4 | **HIGH** | Fat controllers: validação, regra de negócio e acesso direto ao ORM dentro das rotas; `process_task_data` e as constantes de `utils/helpers.py` existem mas não são usados | `routes/task_routes.py:85-154`, `routes/task_routes.py:156-223`, `utils/helpers.py:57-116` | A camada de controller/service não existe de fato, e a lógica não pode ser testada sem HTTP. A organização em pastas é só aparente. |
| 5 | **MEDIUM** | Queries N+1: `User.query.get` e `Category.query.get` por task na listagem, contagem de tasks por usuário e por categoria em loop | `routes/task_routes.py:41-57`, `routes/report_routes.py:55-68`, `routes/report_routes.py:159-164`, `routes/user_routes.py:22` | O número de queries cresce com o volume de dados. Os relacionamentos `task.user`/`task.category` já existem e poderiam usar `joinedload` ou agregação com `GROUP BY`. |
| 6 | **MEDIUM** | APIs deprecated: `Model.query.get()` (legado no SQLAlchemy 2.0) e `datetime.utcnow()` (deprecated no Python 3.12) | `routes/task_routes.py:42`, `routes/task_routes.py:67`, `routes/user_routes.py:29`, `routes/report_routes.py:105`, `models/task.py:15-16`, `models/user.py:14`, `models/category.py:11` (entre outros) | Geram `LegacyAPIWarning`/`DeprecationWarning` e vão quebrar em versões futuras. Os equivalentes modernos são `db.session.get(Model, id)` e `datetime.now(timezone.utc)`. |
| 7 | **MEDIUM** | Lógica de "task atrasada" duplicada em 6 lugares, embora `Task.is_overdue()` já exista | `models/task.py:50-60`, `routes/task_routes.py:30-39`, `routes/task_routes.py:71-80`, `routes/task_routes.py:283-287`, `routes/user_routes.py:171-180`, `routes/report_routes.py:33-43` | É uma violação de DRY: mudar a regra exige alterar 6 pontos, com risco alto de divergência. |
| 8 | **MEDIUM** | `except:` genérico (bare except) e entradas não validadas: `priority` como string gera `TypeError` (500); `PUT /categories/<id>` sem corpo quebra em `'name' in None` | `routes/task_routes.py:62`, `routes/task_routes.py:113`, `routes/report_routes.py:196-197`, `routes/user_routes.py:130`, `utils/helpers.py:46-50` | O bare except engole até `KeyboardInterrupt`/`SystemExit` e esconde bugs. Falta um error handler centralizado e validação de schema (o `marshmallow` está nas dependências e não é usado). |
| 9 | **LOW** | Imports não utilizados: `os, sys, json` no app; `json, os, sys, time` nas rotas; `hashlib, json` em `user_routes`; `format_date`/`calculate_percentage` importados e não usados | `app.py:7`, `routes/task_routes.py:7`, `routes/user_routes.py:6`, `routes/report_routes.py:7-8`, `models/task.py:3`, `utils/helpers.py:3-7` | É ruído que dificulta entender as dependências reais de cada módulo. |
| 10 | **LOW** | Magic values e booleanos verbosos: status, roles, prioridade `1-5` e senha mínima `4` repetidos como literais (as constantes de `helpers.py:110-116` são ignoradas); `if x: return True else: return False` | `routes/task_routes.py:110`, `routes/task_routes.py:113`, `routes/user_routes.py:64`, `routes/user_routes.py:71`, `models/task.py:38-48`, `models/user.py:34-38` | Fica sem fonte única de verdade para as regras, e há código prolixo onde bastaria `return self.role == 'admin'`. |

---

## Construção da Skill

A skill fica em `.claude/skills/refactor-arch/` e tem um `SKILL.md` (orquestração) e 5 arquivos de referência (conhecimento). A fonte da verdade é a cópia de `code-smells-project/`. As outras duas são cópias idênticas, sincronizadas com `rsync -a --delete`.

### Decisões de design

**SKILL.md como orquestrador, referências como conhecimento.** O `SKILL.md` define só o fluxo: as 3 fases, os passos de cada uma, os formatos de saída e as regras que não podem ser quebradas. Catálogo, heurísticas, template e exemplos de código ficam em `references/`. Assim o `SKILL.md` fica curto e fácil de seguir, e dá para evoluir o catálogo sem mexer no fluxo.

**Carregamento sob demanda.** Uma tabela no `SKILL.md` indica *quando* ler cada referência. Por exemplo, o playbook só é lido na Fase 3 e o template só antes de escrever o relatório. Isso economiza contexto e evita que o modelo comece a refatorar enquanto ainda está auditando.

| Arquivo | Fase | Papel |
|---|---|---|
| `project-analysis.md` | 1 | Heurísticas para detectar linguagem, framework, banco, domínio, endpoints e tipo de arquitetura, além de comandos para subir e validar a aplicação |
| `anti-patterns-catalog.md` | 2 | 21 anti-patterns com severidade, sinais de detecção, grep sugerido, casos que **não** são finding, evidência exigida e recomendação |
| `audit-report-template.md` | 2 | Estrutura exata do relatório, regras de preenchimento, um exemplo preenchido e um checklist antes de imprimir |
| `mvc-guidelines.md` | 3 | Camadas, regra de dependência, estrutura alvo por stack e estratégia para projetos já parcialmente organizados |
| `refactoring-playbook.md` | 3 | Uma transformação antes/depois por anti-pattern, com o mesmo ID do catálogo |

**IDs compartilhados (AP-01 a AP-21).** Catálogo e playbook usam os mesmos IDs. Cada finding do relatório aponta direto para a correção correspondente, e na validação final a skill roda o catálogo de novo para conferir que os findings foram eliminados.

**Regras invioláveis explícitas.** O `SKILL.md` abre com 7 regras:
- Fases 1 e 2 são somente leitura.
- A Fase 2 termina com uma pergunta e a skill **para**.
- Todo finding precisa de arquivo e linha conferidos no código.
- Nada de assumir a stack.
- O contrato da API é preservado, salvo correções de segurança, que são listadas.
- Lista de diretórios ignorados.
- O bloco `PHASE 1` é obrigatório: é impresso ao fim da Fase 1 e repetido no início da mensagem final da Fase 2, para não se perder quando mensagens intermediárias não são exibidas.

Também colocamos `disable-model-invocation: true` no frontmatter, para que a skill só rode quando alguém a chamar de propósito e nunca seja acionada por engano numa conversa qualquer.

**Fase 3 com baseline e validação.** Antes de alterar qualquer arquivo, a skill sobe a aplicação original e chama todos os endpoints do inventário da Fase 1. Esse resultado é o baseline. Depois da refatoração ela repete as chamadas e compara status e formato das respostas. Assim, "a aplicação continua funcionando" vira algo verificável e não uma declaração do modelo.

**Saídas com formato fixo.** Os blocos `PHASE 1`, o relatório e `PHASE 3` têm formato definido. Isso deixa a saída previsível entre execuções e permite salvar o relatório direto em `reports/audit-project-N.md`.

### Anti-patterns do catálogo

O catálogo tem 21 entradas. Elas vieram de dois lugares: a análise manual dos 3 projetos, que mostrou quais problemas aparecem de fato em código legado, e a escala de severidade do enunciado, para que cada nível tivesse critérios objetivos. Entraram só problemas que dá para **detectar no código com evidência de linha** e que têm uma **correção concreta** no playbook.

| Severidade | Anti-patterns | Por que entraram |
|---|---|---|
| CRITICAL | AP-01 SQL Injection · AP-02 Segredos hardcoded · AP-03 Senha insegura (texto puro, MD5, cripto caseira) · AP-04 Endpoint sensível sem auth · AP-05 God Class/God File | Permitem comprometer o sistema ou anulam a separação de responsabilidades. Apareceram nos 3 projetos, com variações: SQL concatenado, chave de pagamento *live*, MD5, `/admin/query` aberto |
| HIGH | AP-06 Fat Controller · AP-07 Estado global mutável · AP-08 Acoplamento sem DI · AP-09 Dados sensíveis em respostas/logs | São as violações de MVC/SOLID que impedem testar e evoluir o código. O AP-09 ficou separado do AP-03 porque vazar um dado (senha no JSON, cartão no log) é diferente de armazená-lo mal |
| MEDIUM | AP-10 N+1 · AP-11 Sem transação · AP-12 Validação ausente/duplicada · AP-13 Erro genérico · AP-14 APIs deprecated · AP-15 Callback hell · AP-16 Lógica duplicada | Performance, integridade e robustez. O AP-14 tem uma tabela de API obsoleta → equivalente moderno por stack, e o relatório ganhou uma seção própria de *Deprecated APIs* |
| LOW | AP-17 Magic numbers · AP-18 print/console.log · AP-19 Nomes ruins · AP-20 Código morto · AP-21 Condicionais verbosas | Legibilidade. Entraram porque são baratos de corrigir na refatoração e deixam o resultado limpo |

Cada entrada segue a mesma anatomia: descrição, sinais de detecção por linguagem, grep sugerido, **"Não é finding"**, evidência exigida e recomendação. A seção "Não é finding" foi a decisão mais importante para a precisão. Por exemplo, `.like(f'%{q}%')` do SQLAlchemy não é SQL Injection, porque o ORM parametriza a query. Algumas entradas também têm uma regra de ajuste de severidade. O AP-14, por exemplo, sobe para HIGH quando a API já foi removida na versão declarada.

### Como a skill ficou agnóstica de tecnologia

- **Detecção por evidência, não por suposição.** O `project-analysis.md` traz tabelas de manifesto/import → linguagem/framework para Python, Node/TS, Ruby, PHP, Java, Go e C#. A regra 4 proíbe assumir a stack.
- **Sinais conceituais além dos sintáticos.** Cada anti-pattern tem um sinal "qualquer linguagem" (ex.: "função de acesso a dados recebendo uma única string montada dinamicamente"). O catálogo manda aplicar o *conceito* à sintaxe equivalente quando a linguagem não aparece nos exemplos.
- **Exemplos em duas stacks.** Playbook e guidelines mostram Python/Flask **e** Node/Express lado a lado. Ver o mesmo princípio em duas sintaxes ajuda a generalizar para uma terceira.
- **Estrutura alvo adaptativa.** A Fase 3 distingue o *monolito*, que é desmembrado em camadas, de *camadas parciais*, onde se reaproveita o que já está correto e se criam só as camadas que faltam. As decisões partem da classificação da Fase 1, não de um molde fixo.
- **Sem conhecimento dos 3 projetos.** Nenhum nome de arquivo, linha, rota ou literal deles aparece na skill. Os exemplos usam entidades comuns de CRUD (pedidos, usuários, tasks) e a heurística de domínio cobre vários tipos de sistema, não só os 3 do desafio.
- **Mesma skill, sem alteração, nos 3 projetos.** A cópia é idêntica em dois projetos Flask (um monolito e um em camadas parciais) e num projeto Express, sem nenhum ajuste por projeto.

### Desafios encontrados e soluções

| Desafio | Solução |
|---|---|
| **Números de linha inventados ou aproximados** pelo modelo | Regra 3: só reportar com linha conferida no código, e o template exige um trecho copiado (não parafraseado) como evidência |
| **Falsos positivos de grep** (ORM confundido com SQL injection, constante confundida com segredo) | Grep é ponto de partida e não prova. Cada anti-pattern tem a seção "Não é finding", e a confirmação exige ler o contexto |
| **Findings fragmentados** (o mesmo problema reportado 7 vezes) | Regra de consolidação: mesma causa vira 1 finding com várias localizações, e as contagens do Summary precisam bater |
| **Modelo antecipando a Fase 3** antes da confirmação | Pergunta com texto fixo, instrução explícita de PARAR, proibição de ferramentas de escrita e leitura tardia do playbook |
| **Projeto já parcialmente organizado** (a mesma receita do monolito destruiria o que estava certo) | Seção 5 do `mvc-guidelines.md`: preservar, criar só o que falta, reaproveitar helpers ignorados e justificar desvios no plano |
| **Refatoração que "compila" mas quebra o contrato** | Baseline de todos os endpoints antes da mudança, comparação depois e lista explícita de quebras intencionais (só correções de segurança) |
| **Warnings de deprecação após a refatoração** | Tabela de APIs deprecated por versão no catálogo, e a validação exige subir **sem warnings** |
| **Manter 3 cópias idênticas da skill** | Uma fonte da verdade e sincronização com `rsync -a --delete` |
| **Resumo da Fase 1 omitido** (o modelo trocava o bloco `PHASE 1` por "Fase 1 concluída" e ia direto para a auditoria) | Regra 7: o bloco é obrigatório e é repetido no início da mensagem final da Fase 2, que é sempre exibida ao usuário |
| **Relatório com segredo exposto, Summary sem linha e contagem de arquivos errada** | Regras mais estritas no template (mascarar **todos** os segredos, `arquivo:linha` também no Summary, `Files` igual ao `Source files` da Fase 1) e itens novos no checklist do template |
| **Exemplos vazando os projetos-alvo** (nomes de arquivo, segredos e funções copiados dos projetos para o playbook e o template) | Revisão dos arquivos de referência: os exemplos passaram a usar nomes e literais neutros, e a heurística de domínio foi ampliada para outros tipos de sistema |

## Resultados

A skill foi executada nos 3 projetos com a mesma cópia, sem nenhum ajuste por projeto. Os relatórios completos da Fase 2 estão em [`reports/`](reports/). Eles foram gerados com a versão final da skill sobre o código **original** de cada projeto (commit inicial), antes de qualquer refatoração.

### Resumo das auditorias

| Projeto | Stack detectada | Arquivos analisados | CRITICAL | HIGH | MEDIUM | LOW | Total | Relatório |
|---|---|---|---|---|---|---|---|---|
| code-smells-project | Python + Flask 3.1.1 | 4 (~780 linhas) | 6 | 4 | 5 | 4 | **19** | [audit-project-1.md](reports/audit-project-1.md) |
| ecommerce-api-legacy | JavaScript (Node.js) + Express 4.x | 3 (~180 linhas) | 5 | 4 | 5 | 3 | **17** | [audit-project-2.md](reports/audit-project-2.md) |
| task-manager-api | Python + Flask 3.0.0 | 15 (~1158 linhas) | 4 | 3 | 6 | 5 | **18** | [audit-project-3.md](reports/audit-project-3.md) |

Os 3 projetos atendem aos critérios de aceite: stack detectada corretamente, pelo menos 5 findings e pelo menos 1 CRITICAL ou HIGH. A skill encontrou todos os problemas CRITICAL e HIGH da [Análise Manual](#análise-manual) e vários outros que a análise manual não listou, como acoplamento sem injeção de dependência (AP-08) e código morto (AP-20).

### Estrutura antes e depois

#### Projeto 1 — code-smells-project

Monolito de 4 arquivos → MVC em `src/`, com o `app.py` da raiz mantido como entry point fino.

```
ANTES                         DEPOIS
app.py         (rotas+config) app.py                      ← entry point fino (python app.py)
controllers.py (HTTP+regras)  src/
models.py      (SQL+regras)   ├── app.py                  ← composition root (create_app)
database.py    (conexão global)├── config/settings.py     ← configuração via ambiente
                              ├── database.py             ← conexão por requisição, schema e seed
                              ├── errors.py               ← exceções de domínio
                              ├── models/                 ← produto, usuario, pedido (SQL parametrizado)
                              ├── services/               ← pedido (transação), relatório, notificação
                              ├── controllers/            ← produto, usuario, pedido, sistema
                              ├── views/                  ← blueprints (rotas)
                              ├── validators/             ← validação de entrada por entidade
                              └── middlewares/            ← error handler central e autenticação
```

#### Projeto 2 — ecommerce-api-legacy

God Class `AppManager` → camadas em `src/`, com `src/app.js` como composition root.

```
ANTES                          DEPOIS
src/app.js        (bootstrap)  src/
src/AppManager.js (DB+rotas+   ├── app.js          ← composition root
                   pagamento+  ├── config/         ← variáveis de ambiente e constantes
                   relatório)  ├── database/       ← conexão (Promises + transações), schema e seed
src/utils.js      (segredos+   ├── models/         ← user, course, enrollment, payment, auditLog
                   estado      ├── services/       ← checkout, relatório, usuário, gateway de pagamento
                   global)     ├── controllers/    ← checkout, report, user
                               ├── routes/         ← mapeamento de rotas
                               ├── validators/     ← validação de entrada
                               ├── middlewares/    ← error handler, asyncHandler, auth admin
                               └── utils/          ← hash de senha (scrypt) e logger
```

#### Projeto 3 — task-manager-api

Camadas parciais → camadas completas. A skill reaproveitou `models/`, `routes/` e `services/` e criou só o que faltava.

```
ANTES                              DEPOIS
app.py        (config hardcoded)   app.py          ← composition root (create_app) e entry point
database.py                        config/         ← settings via ambiente e constantes de domínio  [novo]
models/       (MD5, to_dict c/ senha) models/      ← hash seguro, serializer sem senha, consultas agregadas
routes/       (fat controllers)    routes/         ← blueprints finos (categorias e sistema separados)
services/     (SMTP hardcoded)     controllers/    ← fluxo da aplicação                              [novo]
utils/helpers.py (não usado)       services/       ← relatórios e notificações
seed.py                            validators/     ← validação de payloads                           [novo]
                                   middlewares/    ← error handler central e autenticação            [novo]
                                   utils/          ← datetime_utils (substitui o helper morto)
                                   seed.py
```

### Checklist de validação

Legenda: ✅ atendido

| Item | Projeto 1 | Projeto 2 | Projeto 3 |
|---|---|---|---|
| **Fase 1 — Análise** | | | |
| Linguagem detectada corretamente | ✅ Python | ✅ JavaScript (Node.js) | ✅ Python |
| Framework detectado corretamente | ✅ Flask 3.1.1 | ✅ Express 4.x | ✅ Flask 3.0.0 |
| Domínio da aplicação descrito corretamente | ✅ E-commerce (produtos, usuários, pedidos, itens, relatório de vendas) | ✅ LMS com checkout (usuários, cursos, matrículas, pagamentos, logs de auditoria) | ✅ Task Manager (tasks, users, categories, relatórios) |
| Número de arquivos analisados condiz com a realidade | ✅ 4 | ✅ 3 | ✅ 15 |
| **Fase 2 — Auditoria** | | | |
| Relatório segue o template | ✅ | ✅ | ✅ |
| Cada finding tem arquivo e linhas exatos | ✅ | ✅ | ✅ |
| Findings ordenados por severidade | ✅ | ✅ | ✅ |
| Mínimo de 5 findings | ✅ 19 | ✅ 17 | ✅ 18 |
| Detecção de APIs deprecated | ✅ nenhuma no código (seção presente, com o que foi verificado) | ✅ nenhuma no código (seção presente, com o que foi verificado) | ✅ `datetime.utcnow`, `Model.query.get` |
| Skill pausa e pede confirmação antes da Fase 3 | ✅ | ✅ | ✅ |
| **Fase 3 — Refatoração** | | | |
| Estrutura de diretórios segue o padrão MVC | ✅ | ✅ | ✅ |
| Configuração extraída para módulo de config | ✅ `src/config/settings.py` | ✅ `src/config/` | ✅ `config/settings.py` |
| Models criados para abstrair dados | ✅ | ✅ | ✅ |
| Views/Routes separadas | ✅ `src/views/` | ✅ `src/routes/` | ✅ `routes/` |
| Controllers concentram o fluxo da aplicação | ✅ | ✅ | ✅ |
| Error handling centralizado | ✅ | ✅ | ✅ |
| Entry point claro | ✅ `app.py` | ✅ `src/app.js` | ✅ `app.py` |
| Aplicação inicia sem erros | ✅ | ✅ | ✅ |
| Endpoints originais respondem corretamente | ✅ 19/20 (o 20º, `/admin/query`, foi removido de propósito) | ✅ 3/3 | ✅ 22/22 |

### Aplicações rodando após a refatoração

Cada aplicação refatorada foi iniciada com o comando documentado (`python app.py` ou `npm start`) e todos os endpoints originais foram chamados, incluindo os de escrita e os protegidos (com e sem credencial). Os logs abaixo são da execução de validação em 2026-10-13. Para respostas longas, o corpo foi truncado.

<details>
<summary><b>Projeto 1 — code-smells-project</b> (boot + 20 requisições)</summary>

```
2026-10-13 07:53:18,856 INFO src.database: Banco inicializado com dados de exemplo
2026-10-13 07:53:18,859 INFO __main__: Servidor iniciando em http://127.0.0.1:5101
 * Serving Flask app 'src.app'
 * Debug mode: off

200  GET    /                    -> {"endpoints":{"health":"/health","login":"/login","pedidos":"/pedidos",...
200  GET    /health              -> {"ambiente":"development","counts":{"pedidos":0,"produtos":10,"usuarios":3},"database":"connected","status":"ok"...
200  GET    /produtos            -> {"dados":[{"ativo":1,"categoria":"informatica",...
200  GET    /produtos/busca?q=a  -> {"dados":[{"ativo":1,"categoria":"informatica",...
200  GET    /produtos/1          -> {"dados":{"ativo":1,"categoria":"informatica",...
201  POST   /produtos            -> {"dados":{"id":11},"mensagem":"Produto criado","sucesso":true}
200  PUT    /produtos/1          -> {"mensagem":"Produto atualizado","sucesso":true}
200  GET    /usuarios            -> {"dados":[{"criado_em":"...","email":"admin@loja.com","id":1,"nome":"Admin","tipo":"admin"},...   (sem senha)
200  GET    /usuarios/1          -> {"dados":{"criado_em":"...","email":"admin@loja.com","id":1,"nome":"Admin","tipo":"admin"},...
201  POST   /usuarios            -> {"dados":{"id":4},"sucesso":true}
200  POST   /login               -> {"dados":{"email":"admin@loja.com","id":1,"nome":"Admin","tipo":"admin"},"mensagem":"Login OK","sucesso":true,"token":...
201  POST   /pedidos             -> {"dados":{"pedido_id":1,"total":89.9},"mensagem":"Pedido criado com sucesso","sucesso":true}
200  GET    /pedidos             -> {"dados":[{"criado_em":"...","id":1,"itens":[{"preco_unitario":89.9,"produto_id":2,...
200  GET    /pedidos/usuario/2   -> {"dados":[{"criado_em":"...","id":1,"itens":[...
200  PUT    /pedidos/1/status    -> {"mensagem":"Status atualizado","sucesso":true}
200  GET    /relatorios/vendas   -> {"dados":{"desconto_aplicavel":0,"faturamento_bruto":89.9,"faturamento_liquido":89.9,"pedidos_aprovados":1,...
200  DELETE /produtos/3          -> {"mensagem":"Produto deletado","sucesso":true}
401  POST   /admin/reset-db      -> {"erro":"Token ausente","sucesso":false}
200  POST   /admin/reset-db [Bearer admin] -> {"mensagem":"Banco de dados resetado","sucesso":true}
404  POST   /admin/query         -> removido (executava SQL arbitrário)
```
</details>

<details>
<summary><b>Projeto 2 — ecommerce-api-legacy</b> (boot + 7 requisições)</summary>

```
[2026-10-13T10:53:19.220Z] INFO LMS API rodando na porta 3102
[2026-10-13T10:53:23.871Z] INFO Processando pagamento de 497 no cartão ****4444
[2026-10-13T10:53:23.904Z] INFO Processando pagamento de 997 no cartão ****4444

200  POST   /api/checkout                    -> {"msg":"Sucesso","enrollment_id":2}
400  POST   /api/checkout (cartão recusado)  -> Pagamento recusado
400  POST   /api/checkout (payload inválido) -> Bad Request
401  GET    /api/admin/financial-report      -> Unauthorized
200  GET    /api/admin/financial-report [X-Admin-Token] -> [{"course":"Clean Architecture","revenue":997,"students":[{"student":"Leonan","paid":997}]},...
401  DELETE /api/users/1                     -> Unauthorized
200  DELETE /api/users/1 [X-Admin-Token]     -> Usuário deletado com suas matrículas e pagamentos.
```
</details>

<details>
<summary><b>Projeto 3 — task-manager-api</b> (seed + boot + 23 requisições)</summary>

```
$ python seed.py
Seed concluído com sucesso!
  3 usuários
  4 categorias
  10 tasks

$ python app.py
 * Serving Flask app 'app'
 * Debug mode: off

200  GET    /                 -> {"message":"Task Manager API","version":"1.0"}
200  GET    /health           -> {"status":"ok","timestamp":"2026-10-13 07:53:23.521133"}
200  GET    /tasks            -> [{"category_id":1,"category_name":"Backend",...
200  GET    /tasks/1          -> {"category_id":1,"created_at":"...",...
201  POST   /tasks            -> {"category_id":1,"created_at":"...","description":"","due_date":null,"id":11,"overdue":false,...
200  PUT    /tasks/1          -> {"category_id":1,...
200  GET    /tasks/search?q=a -> [{"category_id":1,...
200  GET    /tasks/stats      -> {"cancelled":1,"completion_rate":18.18,"done":2,"in_progress":2,"overdue":1,"pending":6,"total":11}
200  GET    /users            -> [{"active":true,"created_at":"...","email":"joao@email.com","id":1,...   (sem hash de senha)
200  GET    /users/1          -> {"active":true,...
201  POST   /users            -> {"active":true,"created_at":"...","email":"ana@email.com","id":4,"name":"Ana","role":"user"...
200  PUT    /users/2          -> {"active":true,...,"name":"Maria S.",...
200  GET    /users/1/tasks    -> [{"category_id":1,...
200  POST   /login            -> {"message":"Login realizado com sucesso","token":"eyJpZCI6MX0...","user":{...
200  GET    /reports/summary  -> {"generated_at":"...","overdue":{"count":1,"tasks":[...
200  GET    /reports/user/1   -> {"statistics":{"cancelled":0,"completion_rate":20.0,"done":1,"high_priority":3,...
200  GET    /categories       -> [{"color":"#3498db",...,"name":"Backend"...
201  POST   /categories       -> {"color":"#000000",...,"id":5,"name":"Estudos"}
200  PUT    /categories/1     -> {"color":"#3498db",...
200  DELETE /tasks/2          -> {"message":"Task deletada com sucesso"}
200  DELETE /categories/3     -> {"message":"Categoria deletada"}
401  DELETE /users/3          -> {"error":"Autenticação necessária"}
200  DELETE /users/3 [Bearer admin] -> {"message":"Usuário deletado com sucesso"}
```
</details>

#### Mudanças intencionais de contrato

Todas são correções de segurança apontadas na auditoria. As demais rotas mantêm caminho, método, status e formato de resposta.

| Projeto | Mudança | Finding corrigido |
|---|---|---|
| 1 | `POST /admin/query` removido (executava SQL arbitrário) | AP-01, AP-04 |
| 1 | `POST /admin/reset-db` exige token de admin (`Authorization: Bearer`) | AP-04 |
| 1 | `/health` não expõe mais a `SECRET_KEY`; `/usuarios` não retorna senha; `/login` retorna um token assinado | AP-02, AP-09 |
| 2 | `GET /api/admin/financial-report` e `DELETE /api/users/:id` exigem o header `X-Admin-Token` | AP-04 |
| 2 | `DELETE /api/users/:id` remove matrículas e pagamentos na mesma transação (a mensagem de resposta mudou) | AP-11 |
| 3 | `DELETE /users/<id>` e a definição de `role` diferente de `user` exigem token de admin; `/login` retorna token assinado | AP-04 |
| 3 | Respostas de usuário não incluem mais o hash da senha | AP-09 |

### Observações sobre o comportamento da skill em cada stack

- **Monolito Python (projeto 1):** foi o caso mais direto. A skill desmembrou os 4 arquivos em camadas por domínio e manteve o comando `python app.py`, transformando o `app.py` da raiz em um entry point fino. Ela classificou o SQL Injection e o endpoint `/admin/query` como CRITICAL sem precisar de ajuste.
- **Node.js/Express (projeto 2):** os sinais conceituais do catálogo funcionaram sem exemplos específicos de Node, e a skill detectou callback hell (AP-15) e cripto caseira (`badCrypto`, AP-03). Na refatoração, ela converteu o `sqlite3` baseado em callbacks para Promises com async/await e transações. Nas primeiras execuções não interativas (`claude -p`), a skill trocou o bloco `PHASE 1` por uma frase de status ("Fase 1 concluída") e foi direto para a auditoria. A correção foi a regra 7 do `SKILL.md`, que exige repetir o bloco no início da mensagem final da Fase 2. Com ela, o resumo passou a sair completo (domínio: LMS com checkout; 3 arquivos, ~180 linhas; 3 endpoints).
- **Flask com camadas parciais (projeto 3):** a regra de "não reescrever o que já está correto" funcionou. A skill reaproveitou `models/`, `routes/` e `services/`, separou as rotas de categorias do arquivo de relatórios, passou a usar `Task.is_overdue()`, que existia mas era ignorado, e criou só as camadas que faltavam. Foi o único projeto com APIs deprecated de fato, e a validação confirmou o boot sem `DeprecationWarning`.
- **Iterações:** a primeira rodada de relatórios mostrou três falhas: a senha do banco sem máscara na evidência do projeto 2, linhas do Summary do projeto 3 sem `arquivo:linha` (só glob ou nome de API) e a contagem de arquivos do projeto 3 incluindo um arquivo que não era código (16 em vez de 15). As regras 3, 4 e 8 do template e o passo 2 da Fase 1 ficaram mais estritas, e o checklist do template ganhou os itens correspondentes. Na rodada seguinte, as três falhas sumiram. Os números de findings variam um pouco entre execuções (por exemplo, 17 a 19 no projeto 2), mas os CRITICAL e HIGH ficam estáveis.
- **Pontos a melhorar:** no projeto 1, a Fase 1 informou 18 endpoints, mas o código original registra 20 rotas. A contagem não afeta a validação, que chama todas as rotas. Ao rodar `python -W default seed.py` no projeto 3, aparece um `ResourceWarning` de conexão SQLite não fechada no fim do script. Ele não afeta a API.

## Como Executar

### Pré-requisitos

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) instalado e autenticado (`claude --version`)
- Python 3.9+ e `pip` (projetos 1 e 3; o Flask 3.1 exige 3.9+)
- Node.js 18+ e `npm` (projeto 2)
- `curl` ou um cliente HTTP (a extensão REST Client do VS Code lê o `api.http` do projeto 2)

### Executar a skill

A skill fica em `.claude/skills/refactor-arch/` dentro de cada projeto. Abra o Claude Code **no diretório do projeto** e chame a skill:

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

A skill imprime o resumo da Fase 1, gera o relatório da Fase 2 e para em `Proceed with refactoring (Phase 3)? [y/n]`. Salve o relatório em `reports/audit-project-N.md` e responda `y` para refatorar ou `n` para encerrar sem alterar nada.

> Para auditar de novo o código original (os projetos deste repositório já estão refatorados), extraia o commit inicial para outro diretório e copie a skill para dentro dele:
> ```bash
> mkdir -p /tmp/original && git archive 6d1ce62 | tar -x -C /tmp/original
> cp -r code-smells-project/.claude /tmp/original/code-smells-project/
> cd /tmp/original/code-smells-project && claude "/refactor-arch"
> ```

### Validar a refatoração

Cada projeto tem um `.env.example` com as variáveis suportadas. Os detalhes estão no README de cada um.

**Projeto 1 — code-smells-project** (porta 5000)
```bash
cd code-smells-project
pip install -r requirements.txt
python app.py
# em outro terminal
curl -s http://localhost:5000/health
curl -s http://localhost:5000/produtos
curl -s -X POST http://localhost:5000/login -H 'Content-Type: application/json' \
     -d '{"email":"admin@loja.com","senha":"admin123"}'
```

**Projeto 2 — ecommerce-api-legacy** (porta 3000)
```bash
cd ecommerce-api-legacy
npm install
ADMIN_TOKEN=um-token-secreto npm start
# em outro terminal
curl -s -X POST http://localhost:3000/api/checkout -H 'Content-Type: application/json' \
     -d '{"usr":"Ana","eml":"ana@teste.com","pwd":"senhaforte","c_id":1,"card":"4111222233334444"}'
curl -s http://localhost:3000/api/admin/financial-report -H 'X-Admin-Token: um-token-secreto'
```

**Projeto 3 — task-manager-api** (porta 5000)
```bash
cd task-manager-api
pip install -r requirements.txt
python seed.py
python app.py
# em outro terminal
curl -s http://localhost:5000/health
curl -s http://localhost:5000/tasks
curl -s http://localhost:5000/reports/summary
```

Para considerar a refatoração válida, verifique que:
- A aplicação inicia sem erros nem `DeprecationWarning` (nos projetos Python, rode com `python -W default app.py` para exibir os warnings).
- Todos os endpoints listados na Fase 1 respondem com o mesmo status e formato do código original, exceto as mudanças de segurança descritas em [Mudanças intencionais de contrato](#mudanças-intencionais-de-contrato).
- Não há segredos no código. Rodado no diretório do projeto, o comando abaixo não retorna nada (as exclusões ignoram os exemplos da própria skill e as dependências):
  ```bash
  grep -rniE --exclude-dir=.claude --exclude-dir=.venv --exclude-dir=node_modules \
       "secret_key\s*=\s*['\"]|pk_live|debug=True" .
  ```
