<template>
  <div class="dashboard">
    <!-- Welcome Section -->
    <section class="welcome-section">
      <h1 class="welcome-title">
        欢迎回来, <span class="gradient-text">Researcher</span>
      </h1>
      <p class="welcome-subtitle">
        探索心海的奥秘。当前有 <span class="accent">{{ activeSimulations }}</span> 个模拟正在运行。
      </p>
    </section>
    
    <!-- Stats Cards -->
    <section class="stats-grid">
      <xh-card
        v-for="stat in stats"
        :key="stat.label"
        :class="['stat-card', { 'stat-card--highlight': stat.highlight }]"
        hoverable
      >
        <div class="stat-content">
          <div class="stat-icon">{{ stat.icon }}</div>
          <div class="stat-details">
            <span class="stat-value">{{ stat.value }}</span>
            <span class="stat-label">{{ stat.label }}</span>
          </div>
          
          <div v-if="stat.trend" :class="['stat-trend', stat.trend > 0 ? 'up' : 'down']">
            {{ stat.trend > 0 ? '↑' : '↓' }} {{ Math.abs(stat.trend) }}%
          </div>
          
          <div v-if="stat.highlight" class="pulse-indicator"></div>
        </div>
      </xh-card>
    </section>
    
    <!-- Main Grid -->
    <section class="main-grid">
      <!-- Active Simulations -->
      <xh-card title="活跃模拟" class="simulations-panel">
        <template #header-actions>
          <router-link to="/simulation" class="view-all">查看全部 →</router-link>
        </template>
        
        <div class="simulations-list">
          <div
            v-for="sim in recentSimulations"
            :key="sim.id"
            class="simulation-item"
          >
            <div :class="['sim-status', sim.status]">
              <span class="status-dot"></span>
            </div>
            
            <div class="sim-info">
              <div class="sim-name">{{ sim.name }}</div>
              <div class="sim-meta">{{ sim.agents }} 个智能体 · {{ sim.messages }} 条消息</div>
            </div>
            
            <div class="sim-actions">
              <xh-button variant="ghost" size="sm" @click="viewSimulation(sim.id)">
                查看
              </xh-button>
            </div>
          </div>
          
          <div v-if="recentSimulations.length === 0" class="empty-state">
            <div class="empty-icon">🎭</div>
            <p>暂无活跃模拟</p>
            <xh-button variant="primary" @click="createSimulation">创建新模拟</xh-button>
          </div>
        </div>
      </xh-card>
      
      
      <!-- Quick Actions -->
      <xh-card title="快速开始" class="quick-actions">
        <div class="actions-grid">
          <button
            v-for="action in quickActions"
            :key="action.name"
            class="action-btn"
            @click="action.handler"
          >
            <span class="action-icon">{{ action.icon }}</span>
            <span class="action-name">{{ action.name }}</span>
            <span class="action-desc">{{ action.description }}</span>
          </button>
        </div>
      </xh-card>
      
      
      <!-- Recent Activity -->
      <xh-card title="最近活动" class="activity-panel">
        <div class="activity-list">
          <div
            v-for="(activity, index) in recentActivity"
            :key="index"
            class="activity-item"
            :style="{ animationDelay: `${index * 0.1}s` }"
          >
            <div class="activity-icon">{{ activity.icon }}</div>
            <div class="activity-content">
              <div class="activity-text">{{ activity.text }}</div>
              <div class="activity-time">{{ activity.time }}</div>
            </div>
          </div>
        </div>
      </xh-card>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import XhCard from '@/components/ui/XhCard.vue'
import XhButton from '@/components/ui/XhButton.vue'

const router = useRouter()

// 模拟数据
const activeSimulations = ref(3)

const stats = ref([
  { icon: '🎯', value: 128, label: '总会话', trend: 12 },
  { icon: '🤖', value: 24, label: '活跃智能体', trend: 5 },
  { icon: '💬', value: '15.2K', label: '消息数', trend: 28 },
  { icon: '⚡', value: 3, label: '运行中', highlight: true },
])

const recentSimulations = ref([
  {
    id: 1,
    name: 'CBT焦虑治疗模拟',
    status: 'running',
    agents: 3,
    messages: 156
  },
  {
    id: 2,
    name: '自杀风险评估会话',
    status: 'running',
    agents: 2,
    messages: 89
  },
  {
    id: 3,
    name: '多智能体辩论场景',
    status: 'paused',
    agents: 5,
    messages: 234
  }
])

const quickActions = [
  {
    icon: '💬',
    name: '新建对话',
    description: '开始一对一咨询对话',
    handler: () => router.push('/chat')
  },
  {
    icon: '🎭',
    name: '创建模拟',
    description: '设置多智能体模拟场景',
    handler: () => router.push('/simulation')
  },
  {
    icon: '📚',
    name: 'RAG对话',
    description: '基于知识库的智能问答',
    handler: () => router.push('/ragchat')
  },
  {
    icon: '📋',
    name: 'AutoSOP',
    description: '自动化标准操作流程',
    handler: () => router.push('/autosop')
  }
]

const recentActivity = ref([
  { icon: '🤖', text: 'CBT Counselor 完成了一次治疗会话', time: '5分钟前' },
  { icon: '💬', text: '新消息来自 焦虑治疗模拟', time: '12分钟前' },
  { icon: '🎯', text: '创建了新的自杀风险评估会话', time: '1小时前' },
  { icon: '⚡', text: '系统完成了每日数据备份', time: '3小时前' },
  { icon: '📊', text: '生成了本周咨询质量报告', time: '昨天' },
])

const viewSimulation = (id) => {
  router.push(`/simulation?id=${id}`)
}

const createSimulation = () => {
  router.push('/simulation')
}
</script>

<style scoped>
.dashboard {
  max-width: 1400px;
  margin: 0 auto;
}

/* Welcome Section */
.welcome-section {
  margin-bottom: var(--space-2xl);
}

.welcome-title {
  font-size: var(--text-3xl);
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: var(--space-sm);
}

.welcome-subtitle {
  font-size: var(--text-lg);
  color: var(--text-secondary);
}

.accent {
  color: var(--accent-primary);
  font-weight: 600;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--space-lg);
  margin-bottom: var(--space-2xl);
}

.stat-card {
  position: relative;
}

.stat-card--highlight :deep(.xh-card__body) {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(159, 122, 234, 0.1) 100%);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-sm);
}

.stat-icon {
  font-size: 32px;
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 212, 255, 0.1);
  border-radius: var(--radius-lg);
}

.stat-details {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.stat-value {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.stat-trend {
  font-size: var(--text-sm);
  font-weight: 500;
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-sm);
}

.stat-trend.up {
  color: var(--accent-success);
  background: rgba(56, 178, 172, 0.1);
}

.stat-trend.down {
  color: var(--accent-danger);
  background: rgba(255, 107, 107, 0.1);
}

.pulse-indicator {
  position: absolute;
  top: var(--space-md);
  right: var(--space-md);
  width: 10px;
  height: 10px;
  background: var(--accent-success);
  border-radius: 50%;
  animation: pulse-glow 2s ease-in-out infinite;
}

@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 0 5px var(--accent-success);
  }
  50% {
    box-shadow: 0 0 20px var(--accent-success), 0 0 40px var(--accent-success);
  }
}

/* Main Grid */
.main-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  grid-template-rows: auto auto;
  gap: var(--space-lg);
}

.simulations-panel {
  grid-row: span 2;
}

.view-all {
  font-size: var(--text-sm);
  color: var(--accent-primary);
  text-decoration: none;
  transition: opacity var(--transition-fast);
}

.view-all:hover {
  opacity: 0.8;
}

/* Simulations List */
.simulations-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.simulation-item {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md);
  background: rgba(0, 0, 0, 0.2);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.simulation-item:hover {
  background: rgba(0, 212, 255, 0.05);
}

.sim-status {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.sim-status.running .status-dot {
  display: block;
  width: 100%;
  height: 100%;
  background: var(--accent-success);
  border-radius: 50%;
  animation: pulse-glow 2s ease-in-out infinite;
}

.sim-status.paused .status-dot {
  display: block;
  width: 100%;
  height: 100%;
  background: var(--accent-warning);
  border-radius: 50%;
}

.sim-info {
  flex: 1;
}

.sim-name {
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.sim-meta {
  font-size: var(--text-sm);
  color: var(--text-muted);
}

/* Quick Actions */
.actions-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-md);
}

.action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-lg);
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  color: var(--text-primary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.action-btn:hover {
  background: rgba(0, 212, 255, 0.1);
  border-color: rgba(0, 212, 255, 0.3);
  transform: translateY(-2px);
}

.action-icon {
  font-size: 28px;
}

.action-name {
  font-weight: 500;
}

.action-desc {
  font-size: var(--text-xs);
  color: var(--text-muted);
  text-align: center;
}

/* Activity Panel */
.activity-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: var(--space-md);
  padding: var(--space-md);
  background: rgba(0, 0, 0, 0.2);
  border-radius: var(--radius-md);
  animation: fadeInUp 0.5s ease-out forwards;
  opacity: 0;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.activity-icon {
  font-size: 20px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 212, 255, 0.1);
  border-radius: var(--radius-md);
  flex-shrink: 0;
}

.activity-content {
  flex: 1;
}

.activity-text {
  font-size: var(--text-sm);
  color: var(--text-primary);
  margin-bottom: 2px;
}

.activity-time {
  font-size: var(--text-xs);
  color: var(--text-muted);
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-2xl);
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  opacity: 0.5;
}

.empty-state p {
  color: var(--text-secondary);
}

/* Responsive */
@media (max-width: 1024px) {
  .main-grid {
    grid-template-columns: 1fr;
  }
  
  .simulations-panel {
    grid-row: span 1;
  }
}

@media (max-width: 640px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .actions-grid {
    grid-template-columns: 1fr;
  }
}
</style>
