<template>
  <button
    :class="[
      'xh-button',
      `variant-${variant}`,
      `size-${size}`,
      { 
        'is-loading': loading,
        'is-disabled': disabled || loading
      }
    ]"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <!-- Loading Animation -->
    <span v-if="loading" class="loading-indicator">
      <span class="wave-bar"></span>
      <span class="wave-bar"></span>
      <span class="wave-bar"></span>
    </span>
    
    <!-- Icon (left) -->
    <span v-if="iconLeft && !loading" class="icon-left">
      {{ iconLeft }}
    </span>
    
    <!-- Content -->
    <span class="button-content">
      <slot />
    </span>
    
    <!-- Icon (right) -->
    <span v-if="iconRight && !loading" class="icon-right">
      {{ iconRight }}
    </span>
    
    <!-- Ripple Effect -->
    <span v-if="showRipple" class="ripple" :style="rippleStyle"></span>
  </button>
</template>

<script setup>
import { ref, computed } from 'vue'

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
  disabled: Boolean,
  iconLeft: String,
  iconRight: String
})

const emit = defineEmits(['click'])

const showRipple = ref(false)
const rippleStyle = ref({})

function handleClick(event) {
  if (props.loading || props.disabled) return
  
  // Create ripple effect
  const button = event.currentTarget
  const rect = button.getBoundingClientRect()
  const size = Math.max(rect.width, rect.height)
  const x = event.clientX - rect.left - size / 2
  const y = event.clientY - rect.top - size / 2
  
  rippleStyle.value = {
    width: `${size}px`,
    height: `${size}px`,
    left: `${x}px`,
    top: `${y}px`
  }
  
  showRipple.value = true
  setTimeout(() => {
    showRipple.value = false
  }, 600)
  
  emit('click', event)
}
</script>

<style scoped>
.xh-button {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-family: var(--font-sans);
  font-weight: 500;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  overflow: hidden;
  transition: all var(--transition-fast);
  outline: none;
}

/* Variants */
.variant-primary {
  background: linear-gradient(135deg, var(--xh-wave-cyan) 0%, #0891B2 100%);
  color: var(--xh-ocean-deep);
  box-shadow: 0 4px 14px rgba(0, 212, 255, 0.3);
}

.variant-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 212, 255, 0.4);
}

.variant-secondary {
  background: var(--bg-card);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.variant-secondary:hover:not(:disabled) {
  border-color: var(--border-hover);
  background: rgba(30, 58, 95, 0.8);
}

.variant-ghost {
  background: transparent;
  color: var(--text-secondary);
}

.variant-ghost:hover:not(:disabled) {
  background: rgba(0, 212, 255, 0.1);
  color: var(--accent-primary);
}

.variant-danger {
  background: linear-gradient(135deg, var(--xh-mind-coral) 0%, #DC2626 100%);
  color: white;
}

/* Sizes */
.size-sm {
  padding: 8px 16px;
  font-size: 14px;
  height: 36px;
}

.size-md {
  padding: 12px 24px;
  font-size: 16px;
  height: 44px;
}

.size-lg {
  padding: 16px 32px;
  font-size: 18px;
  height: 56px;
}

/* States */
.is-disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.is-loading {
  cursor: wait;
}

/* Loading Animation */
.loading-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  position: absolute;
}

.wave-bar {
  width: 4px;
  height: 16px;
  background: currentColor;
  border-radius: 2px;
  animation: loading-wave 1s ease-in-out infinite;
}

.wave-bar:nth-child(2) {
  animation-delay: 0.1s;
}

.wave-bar:nth-child(3) {
  animation-delay: 0.2s;
}

@keyframes loading-wave {
  0%, 100% {
    transform: scaleY(0.5);
  }
  50% {
    transform: scaleY(1);
  }
}

.is-loading .button-content {
  opacity: 0;
}

/* Ripple Effect */
.ripple {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  transform: scale(0);
  animation: ripple 0.6s ease-out;
  pointer-events: none;
}

@keyframes ripple {
  to {
    transform: scale(4);
    opacity: 0;
  }
}

/* Focus */
.xh-button:focus-visible {
  box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.3);
}

/* Icons */
.icon-left, .icon-right {
  font-size: 1.2em;
  line-height: 1;
}
</style>
