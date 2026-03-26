module.exports = function(app) {
  const { createProxyMiddleware } = require('http-proxy-middleware');
  
  app.use(
    '/openclaw',
    createProxyMiddleware({
      target: 'http://127.0.0.1:18789',
      changeOrigin: true,
      pathRewrite: {
        '^/openclaw': ''
      }
    })
  );
  
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://127.0.0.1:5000',
      changeOrigin: true
    })
  );
};
