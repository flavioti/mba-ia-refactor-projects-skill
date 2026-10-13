const { validateCheckoutPayload } = require('../validators/checkout.validator');

function createCheckoutController({ checkoutService }) {
  return {
    async checkout(req, res) {
      const enrollmentId = await checkoutService.checkout(validateCheckoutPayload(req.body));
      res.status(200).json({ msg: 'Sucesso', enrollment_id: enrollmentId });
    },
  };
}

module.exports = { createCheckoutController };
