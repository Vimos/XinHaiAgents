<template>
  <div class="page-container">
    <xh-card title="⚠️ 自杀风险评估" class="feature-card">
      <p class="description">
        基于CLPsych 2024研究成果的专业自杀风险评估工具，提供6维度综合评估。
      </p>
      
      <div class="features">
        <div class="feature-item">
          <span class="icon">📊</span>
          <div class="content">
            <h4>6维度评估</h4>
            <p>自杀意念、计划、手段、时间、意图、预防因素</p>
          </div>
        </div>
        
        <div class="feature-item">
          <span class="icon">🔬</span>
          <div class="content">
            <h4>证据分级</h4>
            <p>1-4级证据可信度评估，基于临床证据</p>
          </div>
        </div>
        
        <div class="feature-item">
          <span class="icon">⚡</span>
          <div class="content">
            <h4>实时监测</h4>
            <p>对话中实时检测风险信号</p>
          </div>
        </div>
      </div>
      
      <div class="action-section">
        <xh-button variant="danger" @click="startAssessment">
          开始风险评估
        </xh-button>
      </div>
      
      <div class="warning-box">
        <p>⚠️ 此工具仅供专业心理健康工作者使用，评估结果需结合临床判断。</p>
      </div>
    </xh-card>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import XhCard from '@/components/ui/XhCard.vue'
import XhButton from '@/components/ui/XhButton.vue'

const router = useRouter()

const startAssessment = () => {
  router.push('/chat?mode=suicide-risk')
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
  background: rgba(255, 107, 107, 0.1);
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
  margin-bottom: var(--space-lg);
}

.warning-box {
  padding: var(--space-md);
  background: rgba(255, 107, 107, 0.1);
  border: 1px solid rgba(255, 107, 107, 0.3);
  border-radius: var(--radius-md);
  text-align: center;
}

.warning-box p {
  margin: 0;
  color: var(--accent-danger);
  font-size: var(--text-sm);
}
</style>
