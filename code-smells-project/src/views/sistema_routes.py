from flask import Blueprint, jsonify

from src.config.settings import TIPO_ADMIN
from src.middlewares.auth import require_auth


def create_sistema_blueprint(controller):
    bp = Blueprint("sistema", __name__)

    @bp.get("/")
    def index():
        return jsonify(controller.indice())

    @bp.get("/health")
    def health_check():
        return jsonify(controller.health()), 200

    @bp.get("/relatorios/vendas")
    def relatorio_vendas():
        return jsonify({"dados": controller.relatorio_vendas(), "sucesso": True}), 200

    @bp.post("/admin/reset-db")
    @require_auth(tipo=TIPO_ADMIN)
    def reset_database():
        controller.resetar_banco()
        return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200

    return bp
