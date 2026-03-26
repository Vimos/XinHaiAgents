import {createMemoryHistory, createRouter} from 'vue-router'
import DashboardView from "@/views/DashboardView.vue"
import ChatView from "@/views/ChatView.vue"
import RAGChat from "@/views/RAGChat.vue"
import SimulationContainer from "@/views/SimulationContainer.vue"
import CBTView from "@/views/CBTView.vue"
import SuicideRiskView from "@/views/SuicideRiskView.vue"
import EmpathyView from "@/views/EmpathyView.vue"
import CPsyCounView from "@/views/CPsyCounView.vue"

const routes = [
    {path: '/', component: DashboardView, name: 'Dashboard'},
    {path: '/chat', component: ChatView, name: 'Chat'},
    {path: '/cbt', component: CBTView, name: 'CBT'},
    {path: '/suicide-risk', component: SuicideRiskView, name: 'SuicideRisk'},
    {path: '/empathy', component: EmpathyView, name: 'Empathy'},
    {path: '/cpsycoun', component: CPsyCounView, name: 'CPsyCoun'},
    {path: '/simulation', component: SimulationContainer, name: 'Simulation'},
    {path: '/ragchat', component: RAGChat, name: 'RAGChat'},
]

const router = createRouter({
    history: createMemoryHistory(),
    routes,
})

export default router
