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
        
        // 注入环境变量到 DefinePlugin
        config.plugin('define').tap(args => {
            const env = args[0] || {}
            env['process.env'] = {
                ...(env['process.env'] || {}),
                VUE_APP_OPENCLAW_TOKEN: JSON.stringify(process.env.VUE_APP_OPENCLAW_TOKEN || ''),
                VITE_OPENCLAW_TOKEN: JSON.stringify(process.env.VITE_OPENCLAW_TOKEN || '')
            }
            return [env]
        })
    },
    outputDir: 'dist',
    assetsDir: 'static',
    
    devServer: {
        port: 8080,
        proxy: {
            '/openclaw': {
                target: 'http://localhost:18789',
                changeOrigin: true,
                pathRewrite: {
                    '^/openclaw': ''
                }
            }
        }
    }
})
