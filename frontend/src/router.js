import { createMemoryHistory, createRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

import DashboardView from "@/views/DashboardView.vue"
import NewChatView from "@/views/NewChatView.vue"           // 新架构
import NewCBTView from "@/views/NewCBTView.vue"             // 新架构
import NewEmpathyView from "@/views/NewEmpathyView.vue"     // 新架构
import RAGChat from "@/views/RAGChat.vue"
import MultiAgentView from "@/views/MultiAgentView.vue"
import SuicideRiskView from "@/views/SuicideRiskView.vue"
import CPsyCounView from "@/views/CPsyCounView.vue"
import LoginView from "@/views/LoginView.vue"

const routes = [
    { path: '/login', component: LoginView, name: 'Login', meta: { public: true } },
    { path: '/', component: DashboardView, name: 'Dashboard', meta: { requiresAuth: true } },
    { path: '/chat', component: NewChatView, name: 'Chat', meta: { requiresAuth: true } },      // 新架构
    { path: '/cbt', component: NewCBTView, name: 'CBT', meta: { requiresAuth: true } },         // 新架构
    { path: '/empathy', component: NewEmpathyView, name: 'Empathy', meta: { requiresAuth: true } }, // 新架构
    { path: '/suicide-risk', component: SuicideRiskView, name: 'SuicideRisk', meta: { requiresAuth: true } },
    { path: '/cpsycoun', component: CPsyCounView, name: 'CPsyCoun', meta: { requiresAuth: true } },
    { path: '/simulation', component: MultiAgentView, name: 'Simulation', meta: { requiresAuth: true } },
    { path: '/ragchat', component: RAGChat, name: 'RAGChat', meta: { requiresAuth: true } },
]
]

const router = createRouter({
    history: createMemoryHistory(),
    routes,
})

// \u8def\u7531\u5b88\u536b\uff1a\u68c0\u67e5\u767b\u5f55\u72b6\u6001
router.beforeEach((to, from, next) => {
    const authStore = useAuthStore();
    
    // \u5982\u679c\u8def\u7531\u9700\u8981\u8ba4\u8bc1\u4e14\u672a\u767b\u5f55\uff0c\u8df3\u8f6c\u767b\u5f55\u9875
    if (to.meta.requiresAuth && !authStore.isLoggedIn) {
        next('/login');
    }
    // \u5982\u679c\u5df2\u767b\u5f55\u8bbf\u95ee\u767b\u5f55\u9875\uff0c\u8df3\u8f6c\u9996\u9875
    else if (to.meta.public && authStore.isLoggedIn) {
        next('/');
    }
    else {
        next();
    }
})

export default router
