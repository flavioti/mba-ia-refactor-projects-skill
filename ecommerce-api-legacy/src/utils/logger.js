const config = require('../config');

const LEVELS = ['debug', 'info', 'warn', 'error'];
const minLevel = Math.max(LEVELS.indexOf(config.logLevel), 0);

function log(level, args) {
  if (LEVELS.indexOf(level) < minLevel) return;
  const method = level === 'debug' ? 'log' : level;
  console[method](`[${new Date().toISOString()}] ${level.toUpperCase()}`, ...args);
}

module.exports = {
  debug: (...args) => log('debug', args),
  info: (...args) => log('info', args),
  warn: (...args) => log('warn', args),
  error: (...args) => log('error', args),
};
