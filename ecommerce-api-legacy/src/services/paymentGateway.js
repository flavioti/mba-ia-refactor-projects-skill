const { APPROVED_CARD_PREFIX, PAYMENT_STATUS } = require('../config/constants');
const logger = require('../utils/logger');
const { maskCard } = require('../utils/password');

/**
 * Gateway de pagamento simulado. Uma integração real receberia a chave
 * (variável PAYMENT_GATEWAY_KEY) por injeção — nunca a registraria em log.
 */
function createPaymentGateway() {
  return {
    charge(card, amount) {
      logger.info(`Processando pagamento de ${amount} no cartão ${maskCard(card)}`);
      return card.startsWith(APPROVED_CARD_PREFIX) ? PAYMENT_STATUS.PAID : PAYMENT_STATUS.DENIED;
    },
  };
}

module.exports = { createPaymentGateway };
