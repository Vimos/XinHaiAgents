<template>
  <button
    :class="[
      'xh-button',
      `xh-button--${variant}`,
      `xh-button--${size}`,
      { 'xh-button--loading': loading },
      { 'xh-button--disabled': disabled }
    ]"
    :disabled="disabled || loading"
    @click="handleClick"
    @mousedown="createRipple"
  >
    <span v-if="loading" class="xh-button__loading">
      <span class="loading-wave">
        <span></span><span></span><span></span>
      </span>
    </span>
    <span v-else class="xh-button__content">
      <slot />
    </span>
    <span ref="ripple" class="xh-button__ripple"></span>
  </button>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: (v) => ['primary', 'secondary', 'ghost', 'danger'].includes(v)
  },
  size: {
    type: String,
    default: 'md',
    validator: (v) => ['sm', 'md', 'lg'].includes(v)
  },
  loading: Boolean,
  disabled: Boolean
})

const emit = defineEmits(['click'])
const ripple = ref(null)

const handleClick = (e) => {
  if (!props.loading && !props.disabled) {
    emit('click', e)
  }
}

const createRipple = (e) => {
  if (props.disabled || props.loading) return
  
  const button = e.currentTarget
  const rect = button.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  
  const rippleEl = document.createElement('span')
  rippleEl.className = 'ripple'
  rippleEl.style.left = `${x}px`
  rippleEl.style.top = `${y}px`
  
  button.appendChild(rippleEl)
  
  setTimeout(() => {
    rippleEl.remove()
  }, 600)
}
</script>

<style scoped>
.xh-button {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  font-family: var(--font-family);
  font-size: var(--text-base);
  font-weight: 500;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  overflow: hidden;
  transition: all var(--transition-fast);
  outline: none;
}

.xh-button:focus-visible {
  box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.3);
}

/* Variants */
.xh-button--primary {
  background: linear-gradient(135deg, var(--accent-primary) 0%, #0099CC 100%);
  color: var(--bg-primary);
}

.xh-button--primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 212, 255, 0.4);
}

.xh-button--secondary {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.xh-button--secondary:hover:not(:disabled) {
  background: var(--bg-tertiary);
  border-color: var(--accent-primary);
}

.xh-button--ghost {
  background: transparent;
  color: var(--text-secondary);
}

.xh-button--ghost:hover:not(:disabled) {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.xh-button--danger {
  background: var(--accent-danger);
  color: white;
}

.xh-button--danger:hover:not(:disabled) {
  background: #ff5252;
  box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
}

/* Sizes */
.xh-button--sm {
  padding: var(--space-xs) var(--space-sm);
  font-size: var(--text-sm);
}

.xh-button--md {
  padding: var(--space-sm) var(--space-md);
  font-size: var(--text-base);
}

.xh-button--lg {
  padding: var(--space-md) var(--space-lg);
  font-size: var(--text-lg);
}

/* States */
.xh-button--loading,
.xh-button--disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.xh-button__loading {
  display: flex;
  align-items: center;
}

.xh-button__content {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.xh-button__ripple {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

/* Loading animation */
.loading-wave {
  display: flex;
  gap: 3px;
  align-items: center;
  height: 16px;
}

.loading-wave span {
  width: 3px;
  height: 100%;
  background: currentColor;
  border-radius: 2px;
  animation: loading-wave 1s ease-in-out infinite;
}

.loading-wave span:nth-child(2) {
  animation-delay: 0.1s;
}

.loading-wave span:nth-child(3) {
  animation-delay: 0.2s;
}

@keyframes loading-wave {
  0%, 100% {
    transform: scaleY(1);
  }
  50% {
    transform: scaleY(1.5);
  }
}
</style>
