<template>
  <div 
    :class="[
      'xh-avatar',
      `xh-avatar--${size}`,
      { 'xh-avatar--active': isActive },
      { 'xh-avatar--speaking': isSpeaking },
      { 'xh-avatar--thinking': isThinking }
    ]"
  >
    <div class="xh-avatar__image">
      <img 
        v-if="src" 
        :src="src" 
        :alt="name"
        @error="handleImageError"
      />
      <div v-else class="xh-avatar__fallback" :style="{ background: gradient }">
        {{ initials }}
      </div>
    </div>
    
    <!-- 状态指示器 -->
    <div v-if="showStatus" :class="['xh-avatar__status', `xh-avatar__status--${status}`]"></div>
    
    <!-- 说话动画 -->
    <div v-if="isSpeaking" class="xh-avatar__speaking-indicator">
      <span></span><span></span><span></span>
    </div>
    
    <!-- 思考波纹 -->
    <div v-if="isThinking" class="xh-avatar__thinking-ripple"></div>
  </div>
  
  <!-- 信息提示 -->
  <div v-if="showInfo" class="xh-avatar__info">
    <span class="xh-avatar__name">{{ name }}</span>
    <span v-if="role" class="xh-avatar__role">{{ role }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  name: {
    type: String,
    required: true
  },
  role: String,
  src: String,
  size: {
    type: String,
    default: 'md',
    validator: (v) => ['sm', 'md', 'lg', 'xl'].includes(v)
  },
  isActive: Boolean,
  isSpeaking: Boolean,
  isThinking: Boolean,
  status: {
    type: String,
    default: 'offline',
    validator: (v) => ['online', 'offline', 'busy', 'away'].includes(v)
  },
  showStatus: Boolean,
  showInfo: Boolean
})

// 生成名字首字母
const initials = computed(() => {
  return props.name
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
})

// 基于名字生成渐变色
const gradient = computed(() => {
  const colors = [
    ['#00D4FF', '#0099CC'],
    ['#9F7AEA', '#6B46C1'],
    ['#38B2AC', '#2C7A7B'],
    ['#F6E05E', '#D69E2E'],
    ['#FF6B6B', '#C53030'],
    ['#4FD1C5', '#319795']
  ]
  
  // 使用名字字符码之和选择颜色
  const index = props.name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) % colors.length
  const [start, end] = colors[index]
  
  return `linear-gradient(135deg, ${start} 0%, ${end} 100%)`
})

const handleImageError = (e) => {
  e.target.style.display = 'none'
}
</script>

<style scoped>
.xh-avatar {
  position: relative;
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-sm);
}

.xh-avatar__image {
  position: relative;
  border-radius: var(--radius-full);
  overflow: hidden;
  transition: all var(--transition-normal);
}

.xh-avatar__image img,
.xh-avatar__fallback {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: white;
}

/* Sizes */
.xh-avatar--sm .xh-avatar__image {
  width: 32px;
  height: 32px;
}

.xh-avatar--sm .xh-avatar__fallback {
  font-size: var(--text-xs);
}

.xh-avatar--md .xh-avatar__image {
  width: 48px;
  height: 48px;
}

.xh-avatar--md .xh-avatar__fallback {
  font-size: var(--text-base);
}

.xh-avatar--lg .xh-avatar__image {
  width: 64px;
  height: 64px;
}

.xh-avatar--lg .xh-avatar__fallback {
  font-size: var(--text-xl);
}

.xh-avatar--xl .xh-avatar__image {
  width: 96px;
  height: 96px;
}

.xh-avatar--xl .xh-avatar__fallback {
  font-size: var(--text-2xl);
}

/* Active state */
.xh-avatar--active .xh-avatar__image {
  box-shadow: 0 0 0 3px var(--bg-primary), 0 0 0 5px var(--accent-primary);
}

/* Speaking animation */
.xh-avatar--speaking .xh-avatar__image {
  animation: breathe 2s ease-in-out infinite;
}

.xh-avatar__speaking-indicator {
  position: absolute;
  bottom: -8px;
  display: flex;
  gap: 2px;
  padding: 4px 8px;
  background: var(--bg-secondary);
  border-radius: var(--radius-sm);
}

.xh-avatar__speaking-indicator span {
  width: 3px;
  height: 12px;
  background: var(--accent-primary);
  border-radius: 2px;
  animation: sound-wave 0.5s ease-in-out infinite;
}

.xh-avatar__speaking-indicator span:nth-child(2) {
  animation-delay: 0.1s;
}

.xh-avatar__speaking-indicator span:nth-child(3) {
  animation-delay: 0.2s;
}

@keyframes sound-wave {
  0%, 100% {
    transform: scaleY(0.5);
  }
  50% {
    transform: scaleY(1);
  }
}

/* Thinking ripple */
.xh-avatar__thinking-ripple {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100%;
  height: 100%;
  border-radius: var(--radius-full);
  border: 2px solid var(--accent-primary);
  animation: thinking-ripple 1.5s ease-out infinite;
}

@keyframes thinking-ripple {
  0% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 1;
  }
  100% {
    transform: translate(-50%, -50%) scale(1.5);
    opacity: 0;
  }
}

/* Status indicator */
.xh-avatar__status {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 12px;
  height: 12px;
  border-radius: var(--radius-full);
  border: 2px solid var(--bg-primary);
}

.xh-avatar__status--online {
  background: var(--accent-success);
}

.xh-avatar__status--offline {
  background: var(--text-muted);
}

.xh-avatar__status--busy {
  background: var(--accent-danger);
}

.xh-avatar__status--away {
  background: var(--accent-warning);
}

/* Info section */
.xh-avatar__info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.xh-avatar__name {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--text-primary);
}

.xh-avatar__role {
  font-size: var(--text-xs);
  color: var(--text-secondary);
}

@keyframes breathe {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 0 0 3px var(--bg-primary), 0 0 0 5px var(--accent-primary);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 0 0 3px var(--bg-primary), 0 0 0 5px var(--accent-primary), 0 0 20px rgba(0, 212, 255, 0.3);
  }
}
</style>
