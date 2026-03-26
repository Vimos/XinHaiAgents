<template>
  <div 
    :class="[
      'xh-card',
      { 'xh-card--hoverable': hoverable },
      { 'xh-card--glow': glow },
      className
    ]"
    :style="customStyle"
  >
    <div v-if="$slots.header || title" class="xh-card__header">
      <slot name="header">
        <div class="xh-card__title-section">
          <h3 v-if="title" class="xh-card__title">{{ title }}</h3>
          <p v-if="subtitle" class="xh-card__subtitle">{{ subtitle }}</p>
        </div>
      </slot>
    </div>
    
    <div class="xh-card__body">
      <slot />
    </div>
    
    <div v-if="$slots.footer" class="xh-card__footer">
      <slot name="footer" />
    </div>
    
    <!-- Status indicator -->
    <div v-if="status" :class="['xh-card__status', `xh-card__status--${status}`]">
      <span class="status-dot"></span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: String,
  subtitle: String,
  hoverable: {
    type: Boolean,
    default: true
  },
  glow: Boolean,
  status: {
    type: String,
    validator: (v) => ['running', 'paused', 'stopped', 'success', 'error'].includes(v)
  },
  className: String,
  customStyle: Object
})
</script>

<style scoped>
.xh-card {
  position: relative;
  background: rgba(30, 58, 95, 0.6);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(0, 212, 255, 0.15);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: all var(--transition-normal);
}

.xh-card--hoverable:hover {
  transform: translateY(-4px);
  border-color: rgba(0, 212, 255, 0.3);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3), 0 0 20px rgba(0, 212, 255, 0.1);
}

.xh-card--glow {
  box-shadow: 0 0 30px rgba(0, 212, 255, 0.15);
}

.xh-card__header {
  padding: var(--space-md) var(--space-lg);
  border-bottom: 1px solid rgba(0, 212, 255, 0.1);
}

.xh-card__title-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.xh-card__title {
  margin: 0;
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--text-primary);
}

.xh-card__subtitle {
  margin: 0;
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.xh-card__body {
  padding: var(--space-lg);
}

.xh-card__footer {
  padding: var(--space-md) var(--space-lg);
  border-top: 1px solid rgba(0, 212, 255, 0.1);
  background: rgba(0, 0, 0, 0.2);
}

.xh-card__status {
  position: absolute;
  top: var(--space-md);
  right: var(--space-md);
}

.xh-card__status .status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: block;
}

.xh-card__status--running .status-dot {
  background: var(--accent-success);
  box-shadow: 0 0 10px var(--accent-success);
  animation: pulse-glow 2s ease-in-out infinite;
}

.xh-card__status--paused .status-dot {
  background: var(--accent-warning);
}

.xh-card__status--stopped .status-dot {
  background: var(--accent-danger);
}

.xh-card__status--success .status-dot {
  background: var(--accent-success);
}

.xh-card__status--error .status-dot {
  background: var(--accent-danger);
  animation: pulse-glow 1s ease-in-out infinite;
}

@keyframes pulse-glow {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.6;
    transform: scale(1.2);
  }
}
</style>
