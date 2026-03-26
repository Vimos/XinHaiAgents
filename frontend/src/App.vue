<template>
  <div id="app">
    <!-- Ocean Background -->
    <div class="ocean-bg">
      <div class="wave wave-1"></div>
      <div class="wave wave-2"></div>
      <div class="wave wave-3"></div>
    </div>
    
    <!-- Main Layout -->
    <div class="layout">
      <!-- Sidebar -->
      <aside :class="['sidebar', { 'sidebar--collapsed': sidebarCollapsed }]">
        <!-- Logo -->
        <div class="logo">
          <span class="logo__icon">🌊</span>
          <span v-if="!sidebarCollapsed" class="logo__text">心海</span>
        </div>
        
        <!-- Navigation -->
        <nav class="nav">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            :class="['nav__item', { 'nav__item--active': $route.path === item.path }]"
          >
            <span class="nav__icon">{{ item.icon }}</span>
            <span v-if="!sidebarCollapsed" class="nav__label">{{ item.label }}</span>
          </router-link>
        </nav>
        
        <!-- User Profile -->
        <div class="user">
          <div class="user__avatar">
            {{ userInitials }}
          </div>
          <div v-if="!sidebarCollapsed" class="user__info">
            <span class="user__name">{{ username }}</span>
          </div>
        </div>
      </aside>
      
      <!-- Main Content -->
      <main class="main">
        <!-- Header -->
        <header class="header">
          <button class="header__toggle" @click="toggleSidebar">
            <span v-if="sidebarCollapsed">→</span>
            <span v-else>←</span>
          </button>
          
          <div class="header__breadcrumb">
            <span v-for="(crumb, index) in breadcrumbs" :key="index">
              {{ crumb }}
              <span v-if="index < breadcrumbs.length - 1" class="header__separator">/</span>
            </span>
          </div>
          
          <div class="header__actions">
            <xh-button variant="primary" size="sm" @click="createNewSimulation">
              + 新建模拟
            </xh-button>
          </div>
        </header>
        
        <!-- Page Content -->
        <div class="content">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import XhButton from './components/ui/XhButton.vue'

const route = useRoute()

const sidebarCollapsed = ref(false)
const username = ref('Researcher')

const navItems = [
  { path: '/', label: '首页', icon: '🏠' },
  { path: '/chat', label: '心理咨询', icon: '💬' },
  { path: '/cbt', label: 'CBT治疗', icon: '🧠' },
  { path: '/suicide-risk', label: '风险评估', icon: '⚠️' },
  { path: '/empathy', label: '共情对话', icon: '❤️' },
  { path: '/cpsycoun', label: '中文咨询', icon: '📖' },
  { path: '/simulation', label: '多智能体', icon: '🎭' },
  { path: '/ragchat', label: 'RAG问答', icon: '📚' },
]

const userInitials = computed(() => {
  return username.value.split(' ').map(n => n[0]).join('').toUpperCase()
})

const breadcrumbs = computed(() => {
  const path = route.path
  if (path === '/') return ['首页']
  
  const item = navItems.find(i => i.path === path)
  return ['首页', item?.label || '']
})

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

const createNewSimulation = () => {
  // TODO: 打开新建模拟对话框
  console.log('Create new simulation')
}
</script>

<style>
@import './styles/variables.css';
@import './styles/animations.css';

#app {
  min-height: 100vh;
  font-family: var(--font-family);
}

/* Ocean Background */
.ocean-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: -1;
  background: linear-gradient(180deg, #0A1628 0%, #1E3A5F 50%, #0A1628 100%);
}

.wave {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 200%;
  height: 200px;
  background-repeat: repeat-x;
  animation: wave 10s linear infinite;
}

.wave-1 {
  bottom: 0;
  opacity: 0.3;
  animation-duration: 15s;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1440 320'%3E%3Cpath fill='%2300D4FF' fill-opacity='0.1' d='M0,192L48,197.3C96,203,192,213,288,229.3C384,245,480,267,576,250.7C672,235,768,181,864,181.3C960,181,1056,235,1152,234.7C1248,235,1344,181,1392,154.7L1440,128L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z'%3E%3C/path%3E%3C/svg%3E");
}

.wave-2 {
  bottom: 10px;
  opacity: 0.2;
  animation-duration: 12s;
  animation-delay: -2s;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1440 320'%3E%3Cpath fill='%2300D4FF' fill-opacity='0.1' d='M0,64L48,80C96,96,192,128,288,128C384,128,480,96,576,106.7C672,117,768,171,864,176C960,181,1056,139,1152,122.7C1248,107,1344,117,1392,122.7L1440,128L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z'%3E%3C/path%3E%3C/svg%3E");
}

.wave-3 {
  bottom: 20px;
  opacity: 0.1;
  animation-duration: 18s;
  animation-delay: -4s;
}

@keyframes wave {
  0% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(-50%);
  }
}

/* Layout */
.layout {
  display: flex;
  min-height: 100vh;
}

/* Sidebar */
.sidebar {
  width: 240px;
  background: rgba(10, 22, 40, 0.8);
  backdrop-filter: blur(12px);
  border-right: 1px solid rgba(0, 212, 255, 0.1);
  display: flex;
  flex-direction: column;
  transition: width var(--transition-normal);
  z-index: 100;
}

.sidebar--collapsed {
  width: 64px;
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-lg);
  border-bottom: 1px solid rgba(0, 212, 255, 0.1);
}

.logo__icon {
  font-size: 24px;
  flex-shrink: 0;
}

.logo__text {
  font-size: var(--text-xl);
  font-weight: 700;
  background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  white-space: nowrap;
}

.nav {
  flex: 1;
  padding: var(--space-md);
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.nav__item {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  text-decoration: none;
  transition: all var(--transition-fast);
}

.nav__item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.nav__item--active {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.15) 0%, rgba(159, 122, 234, 0.15) 100%);
  color: var(--accent-primary);
  border: 1px solid rgba(0, 212, 255, 0.2);
}

.nav__icon {
  font-size: 20px;
  width: 24px;
  text-align: center;
  flex-shrink: 0;
}

.nav__label {
  font-size: var(--text-base);
  white-space: nowrap;
}

.user {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md);
  border-top: 1px solid rgba(0, 212, 255, 0.1);
}

.user__avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--bg-primary);
  flex-shrink: 0;
}

.user__name {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  white-space: nowrap;
}

/* Main Content */
.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Header */
.header {
  height: 64px;
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: 0 var(--space-lg);
  background: rgba(10, 22, 40, 0.6);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(0, 212, 255, 0.1);
}

.header__toggle {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.header__toggle:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border-color: var(--accent-primary);
}

.header__breadcrumb {
  flex: 1;
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.header__separator {
  margin: 0 var(--space-sm);
  color: var(--text-muted);
}

.header__actions {
  display: flex;
  gap: var(--space-md);
}

/* Content Area */
.content {
  flex: 1;
  padding: var(--space-lg);
  overflow-y: auto;
}

/* Page Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    transform: translateX(-100%);
  }
  
  .sidebar--open {
    transform: translateX(0);
  }
  
  .main {
    margin-left: 0;
  }
}
</style>
