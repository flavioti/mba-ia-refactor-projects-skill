const { validateUserId } = require('../validators/user.validator');

function createUserController({ userService }) {
  return {
    async deleteUser(req, res) {
      await userService.deleteUser(validateUserId(req.params.id));
      res.send('Usuário deletado com suas matrículas e pagamentos.');
    },
  };
}

module.exports = { createUserController };
