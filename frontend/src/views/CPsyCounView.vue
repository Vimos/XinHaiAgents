<template>
  <div class="page-container">
    <xh-card title="📖 中文心理咨询" class="feature-card">
      <p class="description">
        基于CPsyCoun框架的中文专业心理咨询系统，融合9大主题和7大治疗流派。
      </p>
      
      <div class="features">
        <div class="feature-item">
          <span class="icon">📚</span>
          <div class="content">
            <h4>Memo2Demo</h4>
            <p>从咨询报告重建高质量多轮对话</p>
          </div>
        </div>
        
        <div class="feature-item">
          <span class="icon">🎭</span>
          <div class="content">
            <h4>7大流派</h4>
            <p>CBT、人本主义、精神分析、家庭治疗等</p>
          </div>
        </div>
        
        <div class="feature-item">
          <span class="icon">🎯</span>
          <div class="content">
            <h4>9大主题</h4>
            <p>情绪管理、人际关系、职业发展、亲子教育等</p>
          </div>
        </div>
      </div>
      
      <div class="action-section">
        <xh-button variant="primary" @click="startChineseCounseling">
          开始中文咨询
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

const startChineseCounseling = () => {
  router.push('/chat?mode=cpsycoun')
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
  background: rgba(56, 178, 172, 0.1);
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
