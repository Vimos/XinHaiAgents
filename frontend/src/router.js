import {createMemoryHistory, createRouter} from 'vue-router'
import DashboardView from "@/views/DashboardView.vue"
import ChatView from "@/views/ChatView.vue"
import RAGChat from "@/views/RAGChat.vue"
import SimulationContainer from "@/views/SimulationContainer.vue"

const routes = [
    {path: '/', component: DashboardView, name: 'Dashboard'},
    {path: '/chat', component: ChatView, name: 'Chat'},
    {path: '/simulation', component: SimulationContainer, name: 'Simulation'},
    {path: '/ragchat', component: RAGChat, name: 'RAGChat'},
]

const router = createRouter({
    history: createMemoryHistory(),
    routes,
})

export default router
