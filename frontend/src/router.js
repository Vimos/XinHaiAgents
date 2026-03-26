import {createMemoryHistory, createRouter} from 'vue-router'
import DashboardView from "@/views/DashboardView.vue"
import ChatView from "@/views/ChatView.vue"
import RAGChat from "@/views/RAGChat.vue"
import SimulationContainer from "@/views/SimulationContainer.vue"
import AutoSOP from "@/views/AutoSOP.vue"
import AutoInvoice from "@/views/AutoInvoice.vue"

const routes = [
    {path: '/', component: DashboardView, name: 'Dashboard'},
    {path: '/chat', component: ChatView, name: 'Chat'},
    {path: '/simulation', component: SimulationContainer, name: 'Simulation'},
    {path: '/ragchat', component: RAGChat, name: 'RAGChat'},
    {path: '/autosop', component: AutoSOP, name: 'AutoSOP'},
    {path: '/autoinvoice', component: AutoInvoice, name: 'AutoInvoice'},
]

const router = createRouter({
    history: createMemoryHistory(),
    routes,
})

export default router
