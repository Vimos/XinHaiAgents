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
        proxy: {
            '/api*': {
                // Flask backend API
                target: 'http://localhost:5000/'
            },
            '/openclaw*': {
                // OpenClaw Gateway API
                target: 'http://localhost:18789/',
                pathRewrite: { '^/openclaw': '' },
                changeOrigin: true
            }
        }
    }
})
