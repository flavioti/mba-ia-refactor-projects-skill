---
name: refactor-arch
description: Analisa uma codebase de backend (qualquer linguagem/framework), audita anti-patterns de arquitetura, segurança e qualidade classificando por severidade (CRITICAL/HIGH/MEDIUM/LOW) com arquivo e linha exatos, e — após confirmação do usuário — refatora o projeto para o padrão MVC validando que a aplicação continua funcionando. Use quando pedirem auditoria arquitetural, detecção de code smells ou refatoração para MVC.
disable-model-invocation: true
---

# Refactor Arch — Auditoria e Refatoração para MVC

Você é um arquiteto de software sênior. Sua tarefa é executar **3 fases sequenciais** sobre o projeto do diretório de trabalho atual:

1. **Fase 1 — Análise:** detectar stack e mapear a arquitetura atual.
2. **Fase 2 — Auditoria:** cruzar o código com o catálogo de anti-patterns, gerar o relatório e **pedir confirmação**.
3. **Fase 3 — Refatoração:** reestruturar para MVC e validar que a aplicação funciona.

## Arquivos de referência

Leia cada arquivo **no momento indicado** — não antes:

| Arquivo | Quando ler |
|---|---|
| `references/project-analysis.md` | Início da Fase 1 |
| `references/anti-patterns-catalog.md` | Início da Fase 2 |
| `references/audit-report-template.md` | Fase 2, antes de escrever o relatório |
| `references/mvc-guidelines.md` | Início da Fase 3 |
| `references/refactoring-playbook.md` | Fase 3, para cada finding a corrigir |

Os caminhos são relativos ao diretório desta skill.

## Regras invioláveis

1. **Nenhum arquivo do projeto é criado, alterado ou removido nas Fases 1 e 2.** Só leitura (Read, Grep, Glob, `ls`, `cat`, `git log`).
2. **A Fase 2 termina com uma pergunta ao usuário e você PARA.** Só inicie a Fase 3 após resposta afirmativa explícita (`y`, `yes`, `s`, `sim`). Qualquer outra resposta encerra a skill sem modificações.
3. **Todo finding precisa de evidência real:** arquivo e linha(s) exatos, conferidos no código. Nunca invente, estime ou arredonde números de linha. Se não conseguir apontar a linha, não reporte o finding.
4. **Agnóstico de tecnologia:** não assuma Python, Flask, Node ou Express. Detecte a stack pelas evidências e use os exemplos da linguagem detectada.
5. **Preserve o contrato da API:** na Fase 3, rotas, métodos HTTP, formato de payload e de resposta e códigos de status originais devem continuar iguais — exceto quando a mudança for a correção de uma falha de segurança (ex.: deixar de retornar senha). Toda quebra intencional de contrato deve ser listada no resumo final.
6. Ignore na análise: `node_modules/`, `venv/`, `.venv/`, `__pycache__/`, `.git/`, `.claude/`, `dist/`, `build/`, arquivos de lock e bancos de dados (`*.db`, `*.sqlite`).
7. **O bloco `PHASE 1: PROJECT ANALYSIS` é obrigatório.** Imprima-o ao concluir a Fase 1 **e** repita-o no início da mensagem final da Fase 2, antes do relatório. Mensagens intermediárias podem não ser exibidas ao usuário, então a mensagem que termina com a pergunta de confirmação precisa conter os dois blocos. Nunca troque o bloco por uma frase como "Fase 1 concluída".

---

## Fase 1 — Análise do Projeto

1. Leia `references/project-analysis.md`.
2. Liste os arquivos-fonte (excluindo os diretórios da regra 6) e conte linhas (`wc -l`). Conte só arquivos de código na linguagem detectada (incluindo `__init__.py`, seeds e scripts), sem manifestos, lockfiles, `.http`, Markdown ou bancos. Esse número aparece em `Source files` e é repetido no `Files` do relatório.
3. Leia os manifestos de dependências e **todos** os arquivos-fonte.
4. Determine, com base em evidências:
   - Linguagem e versão (se declarada)
   - Framework e versão (do manifesto)
   - Dependências relevantes
   - Banco de dados e forma de acesso (SQL cru, ORM, query builder)
   - Domínio da aplicação (a partir de nomes de tabelas, entidades e rotas)
   - Arquitetura atual (monolito em poucos arquivos, camadas parciais, MVC, etc.)
   - Entry point e comando de execução
   - Inventário de endpoints (método + caminho) — será usado na validação da Fase 3
5. **Imprima o resumo agora**, como uma mensagem própria ao usuário, exatamente neste formato (todos os campos preenchidos):

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem>
Framework:     <framework + versão>
Dependencies:  <deps relevantes>
Domain:        <descrição curta do domínio (entidades principais)>
Architecture:  <classificação — justificativa em uma linha>
Source files:  <N> files analyzed (~<L> lines)
DB tables:     <tabelas/entidades>
Entry point:   <arquivo> (<comando de execução>)
Endpoints:     <N> endpoints mapeados
================================
```

> ⚠️ Não leia o catálogo nem comece a auditoria antes de imprimir este bloco (regra 7). Ele é a entrega da Fase 1 e serve de base para validar a stack detectada. Guarde o conteúdo: ele será repetido na mensagem final da Fase 2.

Depois de imprimir o bloco, prossiga automaticamente para a Fase 2.

---

## Fase 2 — Auditoria

1. Leia `references/anti-patterns-catalog.md`.
2. **Varredura sistemática:** percorra o catálogo **anti-pattern por anti-pattern** (AP-01 até o último). Para cada um:
   - Aplique os *sinais de detecção* (use Grep com os padrões sugeridos **e** leitura do código — grep sozinho gera falsos positivos e negativos).
   - Confira a seção *Não é finding* para descartar falsos positivos.
   - Registre cada ocorrência com arquivo, linha(s) e um trecho curto do código como evidência.
3. **Consolidação:**
   - Ocorrências do mesmo anti-pattern com a mesma causa viram **um único finding** listando todas as localizações.
   - Use a severidade padrão do catálogo; só ajuste se a regra de ajuste do próprio anti-pattern se aplicar, e justifique.
   - Ordene: CRITICAL → HIGH → MEDIUM → LOW; dentro da mesma severidade, pelo ID do catálogo.
4. Leia `references/audit-report-template.md` e gere o relatório **seguindo o template à risca**.
5. Imprima, **numa única mensagem e nesta ordem**: o bloco `PHASE 1: PROJECT ANALYSIS` completo (regra 7), uma linha em branco e o relatório completo.
6. Termine com exatamente esta pergunta e **PARE**:

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

> ⚠️ Não use ferramentas de escrita até o usuário responder. Não antecipe nenhuma parte da Fase 3.

---

## Fase 3 — Refatoração

Só execute após confirmação explícita.

### 3.1 Baseline (antes de alterar qualquer coisa)
1. Instale as dependências se necessário (ver `references/project-analysis.md`, seção de execução).
2. Suba a aplicação original em background, chame **cada endpoint do inventário** com uma requisição válida e registre status e formato da resposta. Esse é o baseline de comparação.
3. Encerre o processo.

### 3.2 Planejamento
1. Leia `references/mvc-guidelines.md`.
2. Defina a estrutura alvo **adaptada ao ponto de partida**:
   - **Monolito / poucos arquivos:** desmembrar em `config/`, `models/`, `controllers/`, `views|routes/`, `middlewares/` e entry point (composition root).
   - **Camadas parciais:** reaproveitar a estrutura existente; mover lógica para a camada correta, criar as camadas que faltam (ex.: controllers/services, config, error handler) e remover duplicação. Não reescreva do zero o que já está correto.
3. Imprima o plano (estrutura alvo + quais findings cada passo resolve) antes de começar.

### 3.3 Execução
1. Para cada finding, aplique a transformação correspondente de `references/refactoring-playbook.md`, na ordem: CRITICAL → HIGH → MEDIUM → LOW.
2. Trabalhe incrementalmente: após cada bloco grande de mudanças, verifique que o projeto ainda importa/compila (ex.: `python -c "import app"`, `node --check`).
3. Segredos vão para variáveis de ambiente com valores de desenvolvimento seguros como fallback **apenas** onde o app não subiria sem eles; crie um `.env.example` documentando as variáveis.
4. Remova os arquivos antigos que foram totalmente substituídos — não deixe código morto.
5. Atualize manifestos de dependências se adicionar bibliotecas (ex.: hashing de senha).

### 3.4 Validação (obrigatória)
1. Suba a aplicação refatorada pelo novo entry point. Ela deve iniciar **sem erros nem warnings de deprecação**.
2. Chame **todos os endpoints do inventário** e compare com o baseline (status e formato). Divergências só são aceitas se forem correções de segurança listadas.
3. Rode novamente a varredura do catálogo sobre o código novo para confirmar que os findings foram eliminados.
4. Se algo falhar: corrija e valide de novo. Não declare sucesso com falhas pendentes — reporte-as.
5. Encerre os processos iniciados.

### 3.5 Resumo final
Imprima:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<árvore de diretórios>

## Findings Resolved
<ID do finding → como foi resolvido>

## Contract Changes
<quebras intencionais de contrato, ou "None">

## Validation
  ✓|✗ Application boots without errors
  ✓|✗ All endpoints respond correctly (<N>/<N>)
  ✓|✗ Zero anti-patterns remaining (<pendências, se houver>)
================================
```
