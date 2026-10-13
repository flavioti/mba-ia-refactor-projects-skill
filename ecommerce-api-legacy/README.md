# ecommerce-api-legacy

LMS API (com fluxo de checkout) em Node.js/Express usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
npm install
ADMIN_TOKEN=um-token-secreto npm start
```

A aplicação sobe em `http://localhost:3000`. O banco SQLite é em memória por padrão e já carrega seeds automaticamente no boot. As variáveis de ambiente suportadas estão documentadas em `.env.example`.

As rotas administrativas (`GET /api/admin/financial-report` e `DELETE /api/users/:id`) exigem o header `X-Admin-Token` com o valor de `ADMIN_TOKEN`. Sem `ADMIN_TOKEN` definido, elas respondem `401`.

Exemplos de requisições estão em `api.http`.

## Estrutura

```
src/
├── app.js            # composition root: cria dependências, registra rotas e inicia o servidor
├── config/           # configuração via variáveis de ambiente + constantes
├── database/         # conexão SQLite (Promises + transações) e schema/seed
├── models/           # acesso a dados por tabela
├── services/         # regras de negócio (checkout, relatório, exclusão de usuário, gateway)
├── controllers/      # fluxo HTTP → service → resposta
├── routes/           # mapeamento de rotas
├── validators/       # validação de entrada
├── middlewares/      # error handler central, asyncHandler, autenticação admin
└── utils/            # hash de senha (scrypt) e logger
```
