<template>
  <div class="page-container">
    <xh-card title="❤️ 共情对话" class="feature-card">
      <p class="description">
        基于APTNESS框架（CIKM 2024）的共情回复生成，结合评估理论和情感支持策略。
      </p>
      
      <div class="features">
        <div class="feature-item">
          <span class="icon">🎨</span>
          <div class="content">
            <h4>情感调色板</h4>
            <p>7大情绪类别 + 23种细分情绪识别</p>
          </div>
        </div>
        
        <div class="feature-item">
          <span class="icon">💡</span>
          <div class="content">
            <h4>17种支持策略</h4>
            <p>提供认可、情感验证、积极重塑等专业策略</p>
          </div>
        </div>
        
        <div class="feature-item">
          <span class="icon">🧩</span>
          <div class="content">
            <h4>评估理论</h4>
            <p>Emotion-Factor-Situation 三维评估框架</p>
          </div>
        </div>
      </div>
      
      <div class="action-section">
        <xh-button variant="primary" @click="startEmpathy">
          开始共情对话
        </xh-button>
      </div>
    </xh-card>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import XhCard from '@/components/ui/XhCard.vue'
import XhButton from '@/components/ui/XhButton.vue'

const router = useRouter()

const startEmpathy = () => {
  router.push('/chat?mode=empathy')
}
</script>

<style scoped>
.page-container {
  padding: var(--space-lg);
  max-width: 900px;
  margin: 0 auto;
}

.description {
  color: var(--text-secondary);
  margin-bottom: var(--space-xl);
  line-height: 1.6;
}

.features {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
  margin-bottom: var(--space-xl);
}

.feature-item {
  display: flex;
  gap: var(--space-md);
  padding: var(--space-md);
  background: rgba(0, 0, 0, 0.2);
  border-radius: var(--radius-md);
  border: 1px solid rgba(0, 212, 255, 0.1);
}

.feature-item .icon {
  font-size: 32px;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(159, 122, 234, 0.1);
  border-radius: var(--radius-md);
}

.feature-item .content h4 {
  margin: 0 0 var(--space-xs) 0;
  color: var(--text-primary);
}

.feature-item .content p {
  margin: 0;
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.action-section {
  display: flex;
  justify-content: center;
  padding-top: var(--space-lg);
  border-top: 1px solid rgba(0, 212, 255, 0.1);
}
</style>
