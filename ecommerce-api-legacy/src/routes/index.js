const express = require('express');

const { asyncHandler } = require('../middlewares/asyncHandler');

function createRouter({ checkoutController, reportController, userController, adminAuth }) {
  const router = express.Router();

  router.post('/checkout', asyncHandler(checkoutController.checkout));
  router.get('/admin/financial-report', adminAuth, asyncHandler(reportController.financialReport));
  router.delete('/users/:id', adminAuth, asyncHandler(userController.deleteUser));

  return router;
}

module.exports = { createRouter };
