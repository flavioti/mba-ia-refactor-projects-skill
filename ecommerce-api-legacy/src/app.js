const express = require('express');

const config = require('./config');
const { createReportController } = require('./controllers/report.controller');
const { createCheckoutController } = require('./controllers/checkout.controller');
const { createUserController } = require('./controllers/user.controller');
const { createConnection } = require('./database/connection');
const { initSchema } = require('./database/schema');
const { createAdminAuth } = require('./middlewares/adminAuth');
const { errorHandler } = require('./middlewares/errorHandler');
const { createAuditLogModel } = require('./models/auditLog.model');
const { createCourseModel } = require('./models/course.model');
const { createEnrollmentModel } = require('./models/enrollment.model');
const { createPaymentModel } = require('./models/payment.model');
const { createUserModel } = require('./models/user.model');
const { createRouter } = require('./routes');
const { createCheckoutService } = require('./services/checkout.service');
const { createPaymentGateway } = require('./services/paymentGateway');
const { createReportService } = require('./services/report.service');
const { createUserService } = require('./services/user.service');
const logger = require('./utils/logger');

/** Composition root: cria as dependências e as injeta em cada camada. */
async function createApp() {
  const db = createConnection(config.dbPath);
  await initSchema(db);

  const userModel = createUserModel(db);
  const courseModel = createCourseModel(db);
  const enrollmentModel = createEnrollmentModel(db);
  const paymentModel = createPaymentModel(db);
  const auditLogModel = createAuditLogModel(db);

  const checkoutService = createCheckoutService({
    db,
    userModel,
    courseModel,
    enrollmentModel,
    paymentModel,
    auditLogModel,
    paymentGateway: createPaymentGateway(),
  });
  const reportService = createReportService({ courseModel });
  const userService = createUserService({ db, userModel, enrollmentModel, paymentModel });

  const app = express();
  app.use(express.json());
  app.use(
    '/api',
    createRouter({
      checkoutController: createCheckoutController({ checkoutService }),
      reportController: createReportController({ reportService }),
      userController: createUserController({ userService }),
      adminAuth: createAdminAuth({ adminToken: config.adminToken }),
    })
  );
  app.use(errorHandler);
  return app;
}

if (require.main === module) {
  createApp()
    .then((app) => {
      app.listen(config.port, () => logger.info(`LMS API rodando na porta ${config.port}`));
    })
    .catch((err) => {
      logger.error('Falha ao iniciar a aplicação:', err);
      process.exit(1);
    });
}

module.exports = { createApp };
