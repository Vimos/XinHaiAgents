<template>
  <div class="page-container">
    <xh-card title="🧠 CBT认知行为治疗" class="feature-card">
      <p class="description">
        基于认知行为疗法（CBT）的专业心理咨询，帮助识别和改变负面思维模式。
      </p>
      
      <div class="features">
        <div class="feature-item">
          <span class="icon">🎯</span>
          <div class="content">
            <h4>5原则督导</h4>
            <p>多智能体协同督导系统，确保咨询质量</p>
          </div>
        </div>
        
        <div class="feature-item">
          <span class="icon">🔍</span>
          <div class="content">
            <h4>认知扭曲识别</h4>
            <p>自动识别来访者的认知偏差和负面思维</p>
          </div>
        </div>
        
        <div class="feature-item">
          <span class="icon">📝</span>
          <div class="content">
            <h4>咨询笔记</h4>
            <p>自动生成结构化CBT咨询记录</p>
          </div>
        </div>
      </div>
      
      <div class="action-section">
        <xh-button variant="primary" @click="startCBT">
          开始CBT咨询
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

const startCBT = () => {
  // 跳转到通用对话，可以传入CBT模式参数
  router.push('/chat?mode=cbt')
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
  background: rgba(0, 212, 255, 0.1);
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
