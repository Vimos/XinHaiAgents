import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ArcoVue from '@arco-design/web-vue';
import App from './App.vue';
import '@arco-design/web-vue/dist/arco.css';
import Axios from 'axios'
import ArcoVueIcon from '@arco-design/web-vue/es/icon';
import router from './router'

import { Message } from '@arco-design/web-vue'

const app = createApp(App);

Message._context = app._context;
app.config.globalProperties.$message = Message;

// \u4f7f\u7528 Pinia \u72b6\u6001\u7ba1\u7406
app.use(createPinia())
    .use(router)
    .use(ArcoVue)
    .use(ArcoVueIcon)
    .mount('#app');
    
app.config.globalProperties.$http = Axios;

// \u5e94\u7528\u542f\u52a8\u65f6\u68c0\u67e5\u767b\u5f55\u72b6\u6001
import { useAuthStore } from '@/stores/auth'
const authStore = useAuthStore()
authStore.init().then(() => {
    console.log('[Auth] Initialization complete')
})
