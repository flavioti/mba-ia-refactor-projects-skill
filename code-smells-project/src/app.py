import logging

from flask import Flask
from flask_cors import CORS

from src import database
from src.config.settings import Settings
from src.controllers.pedido_controller import PedidoController
from src.controllers.produto_controller import ProdutoController
from src.controllers.sistema_controller import SistemaController
from src.controllers.usuario_controller import UsuarioController
from src.middlewares.auth import issue_token
from src.middlewares.error_handler import register_error_handlers
from src.models.pedido_model import PedidoModel
from src.models.produto_model import ProdutoModel
from src.models.usuario_model import UsuarioModel
from src.services.notification_service import NotificationService
from src.services.pedido_service import PedidoService
from src.services.relatorio_service import RelatorioService
from src.views.pedido_routes import create_pedido_blueprint
from src.views.produto_routes import create_produto_blueprint
from src.views.sistema_routes import create_sistema_blueprint
from src.views.usuario_routes import create_usuario_blueprint


def create_app(settings=Settings):
    """Composition root: carrega config, monta as dependências e registra rotas e middlewares."""
    logging.basicConfig(
        level=logging.DEBUG if settings.DEBUG else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    app = Flask(__name__)
    app.config.from_object(settings)
    CORS(app)
    database.init_app(app)
    register_error_handlers(app)

    produto_model = ProdutoModel(database.get_db)
    usuario_model = UsuarioModel(database.get_db)
    pedido_model = PedidoModel(database.get_db)

    pedido_service = PedidoService(produto_model, pedido_model, NotificationService())
    relatorio_service = RelatorioService(pedido_model)

    app.register_blueprint(create_produto_blueprint(ProdutoController(produto_model)))
    app.register_blueprint(create_usuario_blueprint(UsuarioController(usuario_model, issue_token)))
    app.register_blueprint(create_pedido_blueprint(PedidoController(pedido_service, pedido_model)))
    app.register_blueprint(create_sistema_blueprint(SistemaController(
        produto_model,
        usuario_model,
        pedido_model,
        relatorio_service,
        resetar_dados=lambda: database.reset_data(database.get_db()),
        ambiente=settings.APP_ENV,
    )))
    return app
