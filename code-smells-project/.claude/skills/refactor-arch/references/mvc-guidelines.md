# Guidelines de Arquitetura — MVC Alvo

Usado na **Fase 3**. Define as camadas, suas responsabilidades, as dependências permitidas e a estrutura de diretórios alvo por stack. Em APIs REST, a "View" é a camada de **rotas + serialização da resposta** (não há templates HTML).

## 1. Camadas e responsabilidades

| Camada | Responsabilidade | NÃO pode |
|---|---|---|
| **Config** | Ler configuração do ambiente (env vars), valores padrão seguros, constantes da aplicação | Conter lógica de negócio; ter segredos literais |
| **Models** | Entidades/estrutura dos dados, acesso ao banco (repositório), regras intrínsecas da entidade (ex.: `is_overdue()`), serialização segura (`to_dict` sem campos sensíveis) | Conhecer HTTP (`request`, `req`, `res`, `jsonify`, status codes) |
| **Services** *(opcional)* | Regras de negócio que envolvem várias entidades ou efeitos externos (pagamento, email, notificações), transações multi-etapa | Conhecer HTTP |
| **Controllers** | Fluxo da aplicação: receber dados já extraídos da requisição, validar (via validador/schema), chamar models/services, decidir o resultado, lançar erros de domínio | Executar SQL diretamente; formatar detalhes de protocolo além do necessário; conter regras de negócio extensas |
| **Views / Routes** | Mapear método + caminho para o controller; extrair parâmetros da requisição; serializar a resposta (JSON + status) | Conter regra de negócio ou acesso a dados |
| **Middlewares** | Preocupações transversais: tratamento central de erros, autenticação/autorização, logging de requisição, CORS | Regra de negócio |
| **Entry point (composition root)** | Criar a app, carregar config, instanciar dependências (conexão, repositórios, services), injetar, registrar rotas e middlewares, iniciar o servidor | Definir rotas inline ou regras |

**Quando criar Services:** se o controller precisaria coordenar várias entidades, uma transação, ou um efeito externo, extraia para um service. Em domínios simples, controller + model bastam — não crie camadas vazias.

## 2. Regra de dependência

```
Entry point ──► Routes/Views ──► Controllers ──► Services ──► Models ──► Banco
     │                                  │                        ▲
     └──► Config, Middlewares           └────────────────────────┘ (controller pode usar model direto)
```

- Dependências apontam **só para dentro** (para a direita). Model nunca importa controller; controller nunca importa rota.
- Nenhuma camada abaixo de Routes importa objetos de HTTP do framework.
- Dependências externas (conexão, cliente SMTP, gateway) são **injetadas** pelo entry point, não importadas como singletons globais.

## 3. Estrutura alvo — Python/Flask

```
<projeto>/
├── app.py                      # entry point fino: from src.app import create_app; create_app().run(...)
├── requirements.txt
├── .env.example
└── src/
    ├── __init__.py
    ├── app.py                  # create_app(): composition root
    ├── config/
    │   ├── __init__.py
    │   └── settings.py         # Settings lidas de os.environ + constantes
    ├── database.py             # conexão / init do banco / seed (sem estado global mutável)
    ├── models/
    │   ├── __init__.py
    │   └── <entidade>_model.py
    ├── services/               # opcional
    │   └── <dominio>_service.py
    ├── controllers/
    │   ├── __init__.py
    │   └── <dominio>_controller.py
    ├── views/                  # ou routes/
    │   ├── __init__.py
    │   └── <dominio>_routes.py # Blueprints
    ├── validators/             # opcional: schemas de entrada
    └── middlewares/
        ├── __init__.py
        ├── error_handler.py
        └── auth.py             # se houver endpoints protegidos
```

- **Preserve o comando de execução original** (`python app.py`): o `app.py` da raiz vira um entry point fino.
- Use **Blueprints** por domínio; registre-os no `create_app()`.
- Imports absolutos a partir de `src` (`from src.models.order_model import ...`).

## 4. Estrutura alvo — Node.js/Express

```
<projeto>/
├── package.json                # "start" continua apontando para o entry point
├── .env.example
└── src/
    ├── app.js                  # composition root: cria app, injeta deps, registra rotas e error handler, listen
    ├── config/
    │   └── index.js            # config lida de process.env + constantes
    ├── database/
    │   ├── connection.js       # cria conexão, helpers promisificados (run/get/all)
    │   └── schema.js           # criação de tabelas + seed
    ├── models/
    │   └── <entidade>.model.js # factory: createXModel(db) → funções de acesso a dados
    ├── services/               # opcional
    │   └── <dominio>.service.js
    ├── controllers/
    │   └── <dominio>.controller.js
    ├── routes/                 # views
    │   ├── index.js
    │   └── <dominio>.routes.js # express.Router()
    └── middlewares/
        ├── errorHandler.js
        ├── asyncHandler.js
        └── auth.js
```

- Injeção por **factory functions** (`createCheckoutController({ checkoutService })`) ou classes com construtor.
- Use `async/await` com helpers promisificados — sem pirâmides de callbacks.
- Mantenha o script `start` funcionando (ajuste `main`/`start` se o entry point mudar).

## 5. Projetos já parcialmente organizados

Quando já existirem pastas como `models/`, `routes/`, `services/`, `utils/`:

1. **Mantenha** o que está correto (ex.: models do ORM coesos).
2. **Crie** apenas as camadas ausentes (tipicamente `controllers/` ou `services/`, `config/`, `middlewares/error_handler`).
3. **Mova** lógica das rotas para controllers/services; rotas ficam finas.
4. **Reaproveite** helpers/constantes que já existem e estavam ignorados, em vez de criar novos.
5. **Remova** utilitários mortos.
6. Pode manter as pastas na raiz (sem `src/`) se mover tudo quebrar imports sem ganho real — consistência importa mais que o nome da pasta. Justifique no plano.

## 6. Convenções

- **Config:** um único módulo; todo segredo via env; `DEBUG` falso por padrão; documentar variáveis em `.env.example`.
- **Erros:** controllers/services lançam exceções de domínio (`NotFoundError`, `ValidationError`, `ConflictError`, `UnauthorizedError`); o error handler central converte para HTTP. Nada de `try/except` genérico em cada handler.
- **Respostas:** manter o formato original da API (ex.: `{"dados": ..., "sucesso": true}`) — consistência com o contrato existente.
- **Serialização:** um ponto por entidade; nunca expor senha/hash/segredos.
- **Logging:** logger da linguagem com níveis; nada de `print`/`console.log` espalhado.
- **Nomes de arquivos:** Python `snake_case.py`; JS `camelCase.js` ou `<nome>.<camada>.js` — escolha um padrão e use-o em todo o projeto.

## 7. Checklist da estrutura final

- [ ] Estrutura de diretórios segue MVC (models, views/routes, controllers)
- [ ] Configuração extraída para módulo de config (sem hardcoded)
- [ ] Models abstraem os dados (nenhum SQL fora de models/repositórios)
- [ ] Views/Routes só mapeiam e serializam
- [ ] Controllers concentram o fluxo da aplicação
- [ ] Error handling centralizado
- [ ] Entry point claro (composition root)
- [ ] Nenhum import de HTTP fora de routes/controllers/middlewares
- [ ] Nenhum estado global mutável
- [ ] Aplicação inicia sem erros e endpoints originais respondem
