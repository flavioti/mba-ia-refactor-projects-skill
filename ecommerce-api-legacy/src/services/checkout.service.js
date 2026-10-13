const { PAYMENT_STATUS } = require('../config/constants');
const { AppError } = require('../middlewares/errorHandler');
const { hashPassword } = require('../utils/password');

function createCheckoutService({ db, userModel, courseModel, enrollmentModel, paymentModel, auditLogModel, paymentGateway }) {
  return {
    /** Matricula o aluno no curso após pagamento aprovado. Retorna o id da matrícula. */
    async checkout({ name, email, password, courseId, card }) {
      const course = await courseModel.findActiveById(courseId);
      if (!course) throw new AppError('Curso não encontrado', 404);

      const existingUser = await userModel.findByEmail(email);
      if (!existingUser && !password) throw new AppError('Bad Request', 400);

      const status = paymentGateway.charge(card, course.price);
      if (status === PAYMENT_STATUS.DENIED) throw new AppError('Pagamento recusado', 400);

      return db.transaction(async () => {
        const userId = existingUser
          ? existingUser.id
          : await userModel.create({ name, email, passwordHash: hashPassword(password) });
        const enrollmentId = await enrollmentModel.create(userId, course.id);
        await paymentModel.create(enrollmentId, course.price, status);
        await auditLogModel.record(`Checkout curso ${course.id} por ${userId}`);
        return enrollmentId;
      });
    },
  };
}

module.exports = { createCheckoutService };
