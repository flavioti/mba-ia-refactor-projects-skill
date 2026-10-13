const { CARD_NUMBER_PATTERN, EMAIL_PATTERN } = require('../config/constants');
const { AppError } = require('../middlewares/errorHandler');

function isNonEmptyString(value) {
  return typeof value === 'string' && value.trim().length > 0;
}

/**
 * Valida o payload de checkout. Os nomes de campo (usr, eml, pwd, c_id, card)
 * fazem parte do contrato público da API e são mantidos.
 */
function validateCheckoutPayload(body) {
  const { usr: name, eml: email, pwd: password, c_id: rawCourseId, card } = body || {};
  const courseId = Number(rawCourseId);

  const valid =
    isNonEmptyString(name) &&
    isNonEmptyString(email) &&
    EMAIL_PATTERN.test(email) &&
    Number.isInteger(courseId) &&
    courseId > 0 &&
    typeof card === 'string' &&
    CARD_NUMBER_PATTERN.test(card) &&
    (password === undefined || isNonEmptyString(password));

  if (!valid) throw new AppError('Bad Request', 400);

  return { name, email, password, courseId, card };
}

module.exports = { validateCheckoutPayload };
