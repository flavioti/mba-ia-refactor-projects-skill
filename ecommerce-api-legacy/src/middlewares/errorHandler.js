const logger = require('../utils/logger');

class AppError extends Error {
  constructor(message, statusCode = 400) {
    super(message);
    this.statusCode = statusCode;
  }
}

// eslint-disable-next-line no-unused-vars
function errorHandler(err, req, res, next) {
  if (err instanceof AppError) {
    return res.status(err.statusCode).send(err.message);
  }
  if (err.type === 'entity.parse.failed') {
    return res.status(400).send('Bad Request');
  }
  logger.error('Erro inesperado:', err);
  return res.status(500).send('Erro interno');
}

module.exports = { AppError, errorHandler };
