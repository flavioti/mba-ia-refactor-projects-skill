const crypto = require('crypto');

const { AppError } = require('./errorHandler');

/**
 * Exige o header X-Admin-Token igual a ADMIN_TOKEN.
 * Sem ADMIN_TOKEN configurado, as rotas administrativas ficam bloqueadas.
 */
function createAdminAuth({ adminToken }) {
  const expected = Buffer.from(adminToken);

  return (req, res, next) => {
    const received = Buffer.from(req.get('X-Admin-Token') || '');
    const valid =
      expected.length > 0 && received.length === expected.length && crypto.timingSafeEqual(received, expected);
    if (!valid) return next(new AppError('Unauthorized', 401));
    return next();
  };
}

module.exports = { createAdminAuth };
