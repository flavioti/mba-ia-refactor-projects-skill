import logging
import smtplib

from utils.datetime_utils import utcnow

logger = logging.getLogger(__name__)


class NotificationService:
    """Envio de notificações por email. Credenciais injetadas (ver from_config)."""

    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.notifications = []

    @classmethod
    def from_config(cls, config):
        return cls(config["SMTP_HOST"], config["SMTP_PORT"], config["SMTP_USER"], config["SMTP_PASSWORD"])

    def send_email(self, to, subject, body):
        try:
            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.user, self.password)
                server.sendmail(self.user, to, f"Subject: {subject}\n\n{body}")
        except (smtplib.SMTPException, OSError):
            logger.exception("Falha ao enviar email")
            return False
        logger.info("Email enviado: assunto=%r", subject)
        return True

    def notify_task_assigned(self, user, task):
        subject = f"Nova task atribuída: {task.title}"
        body = (
            f"Olá {user.name},\n\nA task '{task.title}' foi atribuída a você.\n\n"
            f"Prioridade: {task.priority}\nStatus: {task.status}"
        )
        self.send_email(user.email, subject, body)
        self.notifications.append(
            {"type": "task_assigned", "user_id": user.id, "task_id": task.id, "timestamp": utcnow()}
        )

    def notify_task_overdue(self, user, task):
        subject = f"Task atrasada: {task.title}"
        body = f"Olá {user.name},\n\nA task '{task.title}' está atrasada!\n\nData limite: {task.due_date}"
        self.send_email(user.email, subject, body)

    def get_notifications(self, user_id):
        return [n for n in self.notifications if n["user_id"] == user_id]
