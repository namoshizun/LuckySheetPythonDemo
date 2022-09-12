const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(
    createProxyMiddleware("/api", {
      // target: 'http://0.0.0.0:8080',
      target: 'http://colabdict-api:8080',
      changeOrigin: true,
      logLevel: "debug",
    })
  );
};
