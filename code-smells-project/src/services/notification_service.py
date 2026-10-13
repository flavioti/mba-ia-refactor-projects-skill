import logging

from src.config.settings import STATUS_APROVADO, STATUS_CANCELADO

logger = logging.getLogger(__name__)


class NotificationService:
    """Simula os canais de notificação (email, SMS, push) registrando no log."""

    def pedido_criado(self, pedido_id, usuario_id):
        logger.info("EMAIL: pedido %s criado para usuario %s", pedido_id, usuario_id)
        logger.info("SMS: pedido %s recebido", pedido_id)
        logger.info("PUSH: novo pedido %s recebido pelo sistema", pedido_id)

    def status_alterado(self, pedido_id, status):
        if status == STATUS_APROVADO:
            logger.info("NOTIFICAÇÃO: pedido %s aprovado, preparar envio", pedido_id)
        elif status == STATUS_CANCELADO:
            logger.info("NOTIFICAÇÃO: pedido %s cancelado, devolver estoque", pedido_id)
