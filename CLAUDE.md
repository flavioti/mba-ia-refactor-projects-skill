# CLAUDE.md

Repositório do desafio de MBA "Criação de Skills — Refatoração Arquitetural Automatizada". O enunciado completo, os critérios de aceite e a análise manual estão no [README.md](README.md).

## Objetivo

Construir a skill `refactor-arch`, que analisa, audita e refatora qualquer projeto para o padrão MVC, de forma agnóstica de tecnologia. Ela roda em 3 fases (análise, auditoria com pausa para confirmação, refatoração com validação) e é aplicada aos 3 projetos legados deste repositório.

## Estrutura

| Diretório | Stack | Como rodar |
|---|---|---|
| `code-smells-project/` | Python/Flask (API de E-commerce) | ver `code-smells-project/README.md` |
| `ecommerce-api-legacy/` | Node.js/Express (LMS API com checkout) | ver `ecommerce-api-legacy/README.md` |
| `task-manager-api/` | Python/Flask + SQLAlchemy (Task Manager) | ver `task-manager-api/README.md` |
| `reports/` | Relatórios da Fase 2 (`audit-project-{1,2,3}.md`) | — |

Cada projeto é independente, com dependências, banco SQLite e `.env.example` próprios. Execute comandos a partir do diretório do projeto.

## Skill `refactor-arch`

- A fonte da verdade é `code-smells-project/.claude/skills/refactor-arch/`. Edite sempre ali.
- `ecommerce-api-legacy/` e `task-manager-api/` têm **cópias idênticas** da skill. Depois de alterar a original, sincronize as cópias (por exemplo, com `rsync -a --delete`).
- O nome `refactor-arch` e o arquivo `SKILL.md` são obrigatórios e não podem ser renomeados.
- Os arquivos de referência ficam em `references/`, em Markdown, e cobrem as 5 áreas exigidas: análise de projeto, catálogo de anti-patterns, template de relatório, guidelines MVC e playbook de refatoração.
- A skill precisa continuar **genérica**. Não coloque nela conhecimento específico de um dos 3 projetos (nomes de arquivos, linhas, domínios); use sinais de detecção que valham para qualquer stack.

## Convenções

- Documentação, relatórios e mensagens de commit em português (PT-BR). Identificadores de código seguem o idioma já usado em cada projeto.
- Ao mudar código de um projeto, valide que ele sobe e que os endpoints originais continuam respondendo. Nenhuma rota ou contrato de API existente pode quebrar.
- Segredos só via variáveis de ambiente. Nada de credenciais no código, e `.env` não é versionado.
- Commits no padrão Conventional Commits (`feat:`, `fix:`, `refactor:`, `docs:`, `chore:`).
