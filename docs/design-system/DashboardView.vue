<template>
  <div class="dashboard-view">
    <!-- Background Effect -->
    <div class="ocean-bg">
      <div class="wave wave-1"></div>
      <div class="wave wave-2"></div>
      <div class="wave wave-3"></div>
    </div>
    
    <!-- Header -->
    <header class="dashboard-header">
      <div class="header-left">
        <div class="logo">
          <span class="logo-icon">🌊</span>
          <span class="logo-text">心海 XinHai</span>
        </div>
        <nav class="main-nav">
          <a href="#" class="nav-item active">Dashboard</a>
          <a href="#" class="nav-item">Sessions</a>
          <a href="#" class="nav-item">Agents</a>
          <a href="#" class="nav-item">Analytics</a>
        </nav>
      </div>
      
      <div class="header-right">
        <button class="btn-new-simulation">
          <span>+</span> New Simulation
        </button>
        <div class="user-menu">
          <img src="/avatar.png" alt="User" class="avatar" />
        </div>
      </div>
    </header>
    
    <!-- Main Content -->
    <main class="dashboard-main">
      <!-- Welcome Section -->
      <section class="welcome-section">
        <h1>Welcome back, Researcher</h1>
        <p class="subtitle">Explore the ocean of minds. {{ activeSimulations }} simulations running.</p>
      </section>
      
      <!-- Stats Cards -->
      <section class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">🎯</div>
          <div class="stat-content">
            <span class="stat-value">{{ stats.totalSessions }}</span>
            <span class="stat-label">Total Sessions</span>
          </div>
          <div class="stat-trend up">+12%</div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">🤖</div>
          <div class="stat-content">
            <span class="stat-value">{{ stats.totalAgents }}</span>
            <span class="stat-label">Active Agents</span>
          </div>
          <div class="stat-trend up">+5%</div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">💬</div>
          <div class="stat-content">
            <span class="stat-value">{{ stats.totalMessages }}</span>
            <span class="stat-label">Messages</span>
          </div>
          <div class="stat-trend up">+28%</div>
        </div>
        
        <div class="stat-card highlight">
          <div class="stat-icon">⚡</div>
          <div class="stat-content">
            <span class="stat-value">{{ stats.runningNow }}</span>
            <span class="stat-label">Running Now</span>
          </div>
          <div class="pulse-indicator"></div>
        </div>
      </section>
      
      <!-- Main Grid -->
      <section class="main-grid">
        <!-- Active Simulations -->
        <div class="panel simulations-panel">
          <div class="panel-header">
            <h3>Active Simulations</h3>
            <a href="#" class="view-all">View All →</a>
          </div>
          
          <div class="simulations-list">
            <div 
              v-for="sim in activeSimulationsList" 
              :key="sim.id"
              class="simulation-item"
            >
              <div class="sim-status" :class="sim.status">
                <span class="status-dot"></span>
              </div>
              
              <div class="sim-info">
                <span class="sim-name">{{ sim.name }}</span>
                <span class="sim-meta">{{ sim.agents }} agents • {{ sim.duration }}</span>
              </div>
              
              <div class="sim-agents">
                <img 
                  v-for="agent in sim.agentAvatars" 
                  :key="agent"
                  :src="agent" 
                  class="agent-avatar"
                  :alt="agent"
                />
              </div>
              
              <button class="btn-enter">Enter</button>
            </div>
          </div>
        </div>
        
        <!-- Quick Start -->
        <div class="panel quickstart-panel">
          <div class="panel-header">
            <h3>Quick Start</h3>
          </div>
          
          <div class="scenario-grid">
            <div 
              v-for="scenario in quickScenarios" 
              :key="scenario.id"
              class="scenario-card"
              @click="startScenario(scenario)"
            >
              <div class="scenario-icon">{{ scenario.icon }}</div>
              <span class="scenario-name">{{ scenario.name }}</span>
              <span class="scenario-desc">{{ scenario.description }}</span>
            </div>
          </div>
        </div>
        
        
        <!-- Network Visualization -->
        <div class="panel viz-panel">
          <div class="panel-header">
            <h3>Agent Network</h3>
            <div class="viz-controls">
              <button class="control-btn">⊕</button>
              <button class="control-btn">⊖</button>
              <button class="control-btn">⟲</button>
            </div>
          </div>
          
          <div class="network-placeholder">
            <div class="network-graph">
              <!-- Network graph visualization would go here -->
              <div class="mock-nodes">
                <div class="mock-node center">Therapist</div>
                <div class="mock-node">Patient 1</div>
                <div class="mock-node">Patient 2</div>
                <div class="mock-node">Patient 3</div>
              </div>
            </div>
          </div>
        </div>
        
        
        <!-- Recent Activity -->
        <div class="panel activity-panel">
          <div class="panel-header">
            <h3>Recent Activity</h3>
          </div>
          
          <div class="activity-list">
            <div 
              v-for="activity in recentActivity" 
              :key="activity.id"
              class="activity-item"
            >
              <div class="activity-icon" :class="activity.type">
                {{ activity.icon }}
              </div>
              
              <div class="activity-content">
                <span class="activity-text">{{ activity.text }}</span>
                <span class="activity-time">{{ activity.time }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// Mock data
const activeSimulations = ref(3)
const stats = ref({
  totalSessions: 127,
  totalAgents: 24,
  totalMessages: 15420,
  runningNow: 3
})

const activeSimulationsList = ref([
  {
    id: 1,
    name: 'Group Therapy Session',
    status: 'running',
    agents: 4,
    duration: '15 min',
    agentAvatars: ['/avatar1.png', '/avatar2.png']
  },
  {
    id: 2,
    name: 'CBT Practice',
    status: 'running',
    agents: 2,
    duration: '8 min',
    agentAvatars: ['/avatar3.png']
  },
  {
    id: 3,
    name: 'Debate Simulation',
    status: 'paused',
    agents: 3,
    duration: '45 min',
    agentAvatars: ['/avatar4.png']
  }
])

const quickScenarios = ref([
  { id: 1, name: 'Therapy Session', icon: '🧠', description: 'One-on-one CBT' },
  { id: 2, name: 'Group Therapy', icon: '👥', description: 'Multi-agent support' },
  { id: 3, name: 'Crisis Intervention', icon: '🚨', description: 'Emergency response' },
  { id: 4, name: 'Debate', icon: '💬', description: 'Structured argument' }
])

const recentActivity = ref([
  { id: 1, type: 'session', icon: '🎯', text: 'Session "CBT Practice" completed', time: '2 min ago' },
  { id: 2, type: 'agent', icon: '🤖', text: 'New agent "Anxiety Patient" created', time: '15 min ago' },
  { id: 3, type: 'system', icon: '⚙️', text: 'System backup completed', time: '1 hour ago' },
  { id: 4, type: 'analysis', icon: '📊', text: 'Analysis report generated', time: '2 hours ago' }
])

function startScenario(scenario) {
  console.log('Starting scenario:', scenario.name)
}
</script>

<style scoped>
.dashboard-view {
  min-height: 100vh;
  background: var(--bg-primary);
  color: var(--text-primary);
  position: relative;
  overflow-x: hidden;
}

/* Ocean Background */
.ocean-bg {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.wave {
  position: absolute;
  width: 200%;
  height: 200%;
  background: radial-gradient(ellipse at center, rgba(0, 212, 255, 0.03) 0%, transparent 70%);
  animation: wave-float 20s ease-in-out infinite;
}

.wave-1 {
  top: -50%;
  left: -50%;
  animation-delay: 0s;
}

.wave-2 {
  top: -30%;
  right: -50%;
  animation-delay: -7s;
}

.wave-3 {
  bottom: -50%;
  left: -30%;
  animation-delay: -14s;
}

@keyframes wave-float {
  0%, 100% {
    transform: translate(0, 0) rotate(0deg);
  }
  33% {
    transform: translate(30px, -30px) rotate(2deg);
  }
  66% {
    transform: translate(-20px, 20px) rotate(-1deg);
  }
}

/* Header */
.dashboard-header {
  position: relative;
  z-index: 10;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 32px;
  background: rgba(10, 22, 40, 0.8);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border-color);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 48px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 24px;
  font-weight: 700;
}

.logo-icon {
  font-size: 32px;
}

.main-nav {
  display: flex;
  gap: 32px;
}

.nav-item {
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
  position: relative;
}

.nav-item:hover,
.nav-item.active {
  color: var(--text-primary);
}

.nav-item.active::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--accent-primary);
  border-radius: 1px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.btn-new-simulation {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: linear-gradient(135deg, var(--xh-wave-cyan), #0891B2);
  color: var(--xh-ocean-deep);
  border: none;
  border-radius: var(--radius-md);
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.btn-new-simulation:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 212, 255, 0.4);
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid var(--border-color);
}

/* Main Content */
.dashboard-main {
  position: relative;
  z-index: 1;
  padding: 32px;
  max-width: 1600px;
  margin: 0 auto;
}

/* Welcome Section */
.welcome-section {
  margin-bottom: 32px;
}

.welcome-section h1 {
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 8px;
  background: linear-gradient(135deg, var(--text-primary), var(--accent-primary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  color: var(--text-secondary);
  font-size: 18px;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  position: relative;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-glow);
}

.stat-card.highlight {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(159, 122, 234, 0.1));
  border-color: var(--accent-primary);
}

.stat-icon {
  width: 48px;
  height: 48px;
  background: rgba(0, 212, 255, 0.1);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
}

.stat-trend {
  position: absolute;
  top: 16px;
  right: 16px;
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-weight: 600;
}

.stat-trend.up {
  background: rgba(56, 178, 172, 0.2);
  color: var(--xh-success-teal);
}

.pulse-indicator {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 12px;
  height: 12px;
  background: var(--xh-success-teal);
  border-radius: 50%;
  animation: pulse-glow 2s ease-in-out infinite;
}

/* Main Grid */
.main-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  grid-template-rows: auto auto;
  gap: 24px;
}

.panel {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
}

.panel-header h3 {
  font-size: 18px;
  font-weight: 600;
}

.view-all {
  color: var(--accent-primary);
  text-decoration: none;
  font-size: 14px;
}

.view-all:hover {
  text-decoration: underline;
}

/* Simulations Panel */
.simulations-panel {
  grid-row: span 2;
}

.simulations-list {
  padding: 16px;
}

.simulation-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border-radius: var(--radius-md);
  transition: background 0.2s;
}

.simulation-item:hover {
  background: rgba(0, 212, 255, 0.05);
}

.sim-status {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sim-status.running .status-dot {
  width: 8px;
  height: 8px;
  background: var(--xh-success-teal);
  border-radius: 50%;
  animation: pulse-glow 2s ease-in-out infinite;
}

.sim-status.paused .status-dot {
  width: 8px;
  height: 8px;
  background: var(--xh-mind-coral);
  border-radius: 50%;
}

.sim-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.sim-name {
  font-weight: 600;
  color: var(--text-primary);
}

.sim-meta {
  font-size: 13px;
  color: var(--text-secondary);
}

.sim-agents {
  display: flex;
}

.agent-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 2px solid var(--bg-card);
  margin-left: -8px;
}

.agent-avatar:first-child {
  margin-left: 0;
}

.btn-enter {
  padding: 8px 16px;
  background: transparent;
  color: var(--accent-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s;
}

.btn-enter:hover {
  background: rgba(0, 212, 255, 0.1);
  border-color: var(--accent-primary);
}

/* Quick Start Panel */
.scenario-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  padding: 16px;
}

.scenario-card {
  background: rgba(30, 58, 95, 0.4);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.scenario-card:hover {
  border-color: var(--accent-primary);
  background: rgba(0, 212, 255, 0.1);
  transform: translateY(-2px);
}

.scenario-icon {
  font-size: 32px;
}

.scenario-name {
  font-weight: 600;
  color: var(--text-primary);
}

.scenario-desc {
  font-size: 13px;
  color: var(--text-secondary);
  text-align: center;
}

/* Viz Panel */
.viz-panel {
  grid-column: span 2;
}

.viz-controls {
  display: flex;
  gap: 8px;
}

.control-btn {
  width: 32px;
  height: 32px;
  background: rgba(30, 58, 95, 0.6);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.control-btn:hover {
  border-color: var(--accent-primary);
  color: var(--text-primary);
}

.network-placeholder {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(0, 212, 255, 0.05) 0%, transparent 70%);
}

.mock-nodes {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 40px;
  position: relative;
}

.mock-node {
  width: 80px;
  height: 80px;
  background: var(--bg-secondary);
  border: 2px solid var(--border-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  text-align: center;
}

.mock-node.center {
  width: 100px;
  height: 100px;
  border-color: var(--accent-primary);
  box-shadow: var(--shadow-glow);
}

/* Activity Panel */
.activity-list {
  padding: 16px;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-color);
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-icon {
  width: 40px;
  height: 40px;
  background: rgba(30, 58, 95, 0.6);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.activity-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.activity-text {
  color: var(--text-primary);
  font-size: 14px;
}

.activity-time {
  color: var(--text-secondary);
  font-size: 12px;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .main-grid {
    grid-template-columns: 1fr;
  }
  
  .simulations-panel {
    grid-row: span 1;
  }
  
  .viz-panel {
    grid-column: span 1;
  }
}

@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    gap: 16px;
    padding: 16px;
  }
  
  .header-left {
    flex-direction: column;
    gap: 16px;
  }
  
  .main-nav {
    gap: 16px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .dashboard-main {
    padding: 16px;
  }
}
</style>
