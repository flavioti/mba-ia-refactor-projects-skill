const { AppError } = require('../middlewares/errorHandler');

function createUserService({ db, userModel, enrollmentModel, paymentModel }) {
  return {
    /** Remove o usuário com suas matrículas e pagamentos, de forma atômica. */
    async deleteUser(userId) {
      const user = await userModel.findById(userId);
      if (!user) throw new AppError('Usuário não encontrado', 404);

      await db.transaction(async () => {
        await paymentModel.deleteByUserId(userId);
        await enrollmentModel.deleteByUserId(userId);
        await userModel.deleteById(userId);
      });
    },
  };
}

module.exports = { createUserService };
