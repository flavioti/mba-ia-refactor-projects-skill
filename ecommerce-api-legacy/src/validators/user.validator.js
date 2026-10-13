const { AppError } = require('../middlewares/errorHandler');

function validateUserId(rawId) {
  const userId = Number(rawId);
  if (!Number.isInteger(userId) || userId <= 0) throw new AppError('Bad Request', 400);
  return userId;
}

module.exports = { validateUserId };
