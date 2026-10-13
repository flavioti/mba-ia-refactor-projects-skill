const sqlite3 = require('sqlite3');

/**
 * Conexão SQLite com API baseada em Promises e transações serializadas.
 */
function createConnection(path) {
  const raw = new sqlite3.Database(path);
  let transactionQueue = Promise.resolve();

  const db = {
    run(sql, params = []) {
      return new Promise((resolve, reject) => {
        raw.run(sql, params, function onRun(err) {
          if (err) return reject(err);
          return resolve({ lastID: this.lastID, changes: this.changes });
        });
      });
    },

    get(sql, params = []) {
      return new Promise((resolve, reject) => {
        raw.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)));
      });
    },

    all(sql, params = []) {
      return new Promise((resolve, reject) => {
        raw.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)));
      });
    },

    /** Executa `work` dentro de BEGIN/COMMIT, com ROLLBACK em caso de erro. */
    transaction(work) {
      const result = transactionQueue.then(async () => {
        await db.run('BEGIN');
        try {
          const value = await work();
          await db.run('COMMIT');
          return value;
        } catch (err) {
          await db.run('ROLLBACK');
          throw err;
        }
      });
      transactionQueue = result.catch(() => {});
      return result;
    },

    close() {
      return new Promise((resolve, reject) => raw.close((err) => (err ? reject(err) : resolve())));
    },
  };

  return db;
}

module.exports = { createConnection };
