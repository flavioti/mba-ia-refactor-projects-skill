import logging

from src.errors import NotFoundError, UnauthorizedError
from src.validators.usuario_validator import validar_login, validar_novo_usuario

logger = logging.getLogger(__name__)


class UsuarioController:
    def __init__(self, usuario_model, emitir_token):
        self._usuarios = usuario_model
        self._emitir_token = emitir_token

    def listar(self):
        return self._usuarios.listar()

    def obter(self, usuario_id):
        usuario = self._usuarios.buscar_por_id(usuario_id)
        if usuario is None:
            raise NotFoundError("Usuário não encontrado")
        return usuario

    def criar(self, dados):
        novo = validar_novo_usuario(dados)
        usuario_id = self._usuarios.criar(novo["nome"], novo["email"], novo["senha"])
        logger.info("Usuário criado com ID %s", usuario_id)
        return usuario_id

    def login(self, dados):
        credenciais = validar_login(dados)
        usuario = self._usuarios.autenticar(credenciais["email"], credenciais["senha"])
        if usuario is None:
            logger.info("Falha de login")
            raise UnauthorizedError("Email ou senha inválidos")
        logger.info("Login bem-sucedido para usuario_id=%s", usuario["id"])
        return usuario, self._emitir_token(usuario)
