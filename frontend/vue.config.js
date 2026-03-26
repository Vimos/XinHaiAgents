const {defineConfig} = require('@vue/cli-service')

module.exports = defineConfig({
    transpileDependencies: true,
    chainWebpack: config => {
        config
            .plugin('html')
            .tap(args => {
                args[0].title = 'XinHaiAgents - 心海多智能体系统'
                return args
            })
        const svgRule = config.module.rule('svg')

        svgRule.uses.clear()

        svgRule
            .use('babel-loader')
            .loader('babel-loader')
            .end()
            .use('vue-svg-loader')
            .loader('vue-svg-loader')
    },
    outputDir: 'dist',
    assetsDir: 'static',
    devServer: {
        port: 8080,
        proxy: {
            '/api': {
                target: 'http://localhost:5000',
                changeOrigin: true,
                logLevel: 'debug'
            },
            '/openclaw': {
                target: 'http://localhost:18789',
                pathRewrite: { '^/openclaw': '' },
                changeOrigin: true,
                logLevel: 'debug',
                onProxyReq: (proxyReq, req) => {
                    console.log('[Proxy]', req.method, req.url, '->', 'http://localhost:18789' + proxyReq.path);
                }
            }
        }
    }
})
