# Template do Relatório de Auditoria

Usado na **Fase 2**. O relatório deve seguir **exatamente** a estrutura abaixo. Ele é impresso no terminal e deve poder ser salvo como Markdown sem edição (ex.: `reports/audit-project-N.md`).

## Regras de preenchimento

1. **Ordem:** CRITICAL → HIGH → MEDIUM → LOW. Dentro da mesma severidade, ordenar pelo ID do catálogo (AP-xx).
2. **Numeração:** findings numerados sequencialmente (`F-01`, `F-02`, …) na ordem final.
3. **Localização:** sempre `arquivo:linha` ou `arquivo:inicio-fim`, com caminho relativo à raiz do projeto. Várias localizações → uma por linha na lista `File:`. Isso vale também para a coluna `Location` do Summary: nunca use só o nome do arquivo, glob (`routes/*.py`), nome de API ou texto como "multiple". Se houver muitas localizações, cite as 2 ou 3 principais com linha e acrescente `+N` (ex.: `` `routes/a.py:42`, `routes/b.py:29` +7 ``).
4. **Evidência:** trecho curto (1–3 linhas) do código real, copiado — não parafraseado. Mascare **todos** os segredos do trecho (senhas, chaves de API, tokens, secret keys, credenciais de banco/SMTP, connection strings), mantendo no máximo os 4 primeiros caracteres: `"sk_l***"`, `"senh***"`. Se o trecho tem vários segredos, mascare cada um. Nunca reproduza um segredo completo em nenhuma parte do relatório.
5. **Summary:** as contagens devem bater exatamente com os findings listados.
6. **Deprecated APIs:** a seção é obrigatória. Se não houver nenhuma, escreva `None detected` e liste o que foi verificado.
7. **Idioma:** títulos/rótulos em inglês (como abaixo); descrições podem estar no idioma do usuário.
8. **Arquivos e linhas:** `Files` usa exatamente o mesmo número de arquivos e linhas do bloco `PHASE 1`. Conte só arquivos de código na linguagem detectada (ex.: `.py`, `.js`, `.ts`, incluindo `__init__.py`), sem manifestos, lockfiles, `.http`, Markdown ou bancos. Linhas = soma do `wc -l` desses arquivos, arredondada com `~`.

## Template

````markdown
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome do diretório>
Stack:   <Linguagem> + <Framework versão>
Files:   <N> analyzed | ~<L> lines of code
Date:    <AAAA-MM-DD>

## Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

| # | Severity | Anti-pattern | Location |
|---|---|---|---|
| F-01 | CRITICAL | <nome> (AP-xx) | `<arquivo:linhas>` |
| ... | ... | ... | ... |

## Findings

### F-01 [CRITICAL] <Nome do anti-pattern>
Catalog: AP-xx
File:
- <arquivo>:<linha|inicio-fim>
- <arquivo>:<linha|inicio-fim>
Evidence:
```<linguagem>
<trecho real do código>
```
Description: <o que está errado, especificamente neste projeto>
Impact: <consequência concreta — o que pode acontecer>
Recommendation: <correção proposta; referência ao playbook AP-xx>

### F-02 [HIGH] <...>
...

## Deprecated APIs
| Location | Deprecated API | Modern replacement |
|---|---|---|
| `<arquivo:linha>` | `<api antiga>` | `<api moderna>` |

## Architecture Overview
Current:  <classificação atual — uma linha>
Target:   MVC — <resumo da estrutura alvo>
Key moves:
- <principal mudança estrutural 1>
- <principal mudança estrutural 2>

================================
Total: <N> findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
````

## Exemplo de finding preenchido

````markdown
### F-01 [CRITICAL] SQL Injection
Catalog: AP-01
File:
- src/repository.py:42
- src/repository.py:87-89
Evidence:
```python
cursor.execute(
    "SELECT * FROM accounts WHERE email = '" + email + "' AND password = '" + password + "'"
)
```
Description: Queries montadas por concatenação de strings com dados vindos do body/rota.
Impact: Login sem senha com `' OR 1=1 --`; leitura e destruição arbitrária de tabelas.
Recommendation: Usar queries parametrizadas (`?` + tupla de parâmetros). Ver playbook AP-01.
````

## Checklist antes de imprimir

- [ ] Toda linha citada foi conferida no arquivo (Read com número de linha).
- [ ] Nenhum finding sem evidência.
- [ ] Toda linha do Summary tem pelo menos um `arquivo:linha`.
- [ ] Nenhum segredo aparece completo (procure senhas, chaves e tokens nas evidências).
- [ ] `Files` bate com o `Source files` da Fase 1.
- [ ] Contagens do Summary = findings listados = Total.
- [ ] Ordenação por severidade correta.
- [ ] Seção Deprecated APIs presente.
- [ ] Nenhum arquivo foi modificado.
- [ ] Termina com a pergunta de confirmação.
