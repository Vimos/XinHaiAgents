<template>
  <div class="cbt-view">
    <div class="cbt-header">
      <h2>🧠 CBT 认知行为治疗</h2>
      <p>通过对话进行认知行为疗法，帮助你识别和改变负面思维模式</p>
    </div>
    
    <ChatPanel
      :messages="chat.messages.value"
      :is-loading="chat.isLoading.value"
      :error="chat.error.value"
      :sessions="chat.sessions.value"
      :current-session-key="chat.sessionKey.value"
      show-sidebar
      :welcome-title="'CBT 治疗对话'"
      :welcome-description="'和我分享你的困扰，我会用认知行为疗法的方法帮助你'"
      :placeholder="'描述你现在的感受或困扰...'"
      @send="handleSend"
      @new-chat="chat.createNewSession"
      @select-session="chat.loadSession"
      @delete-session="chat.deleteSession"
    >
      <template #welcome>
        <div class="cbt-welcome">
          <div class="welcome-icon">🧠</div>
          <h2>CBT 认知行为治疗</h2>
          <p>一个安全的对话空间，通过认知行为疗法帮助你</p>
          
          <div class="cbt-features">
            <div class="feature">
              <span class="feature-icon">🔍</span>
              <span>识别负面思维模式</span>
            </div>
            <div class="feature">
              <span class="feature-icon">🔄</span>
              <span>重构认知框架</span>
            </div>
            <div class="feature">
              <span class="feature-icon">💪</span>
              <span>建立应对策略</span>
            </div>
          </div>
          
          <div class="quick-starts">
            <button 
              v-for="prompt in cbtPrompts" 
              :key="prompt"
              @click="handleSend(prompt)"
            >
              {{ prompt }}
            </button>
          </div>
        </div>
      </template>
    </ChatPanel>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useChat } from '@/composables/useChat.js';
import ChatPanel from '@/components/ChatPanel.vue';

// ============ Setup ============
const SIDEBAR = 'cbt'; // 独立的 sidebar，与其他页面隔离

const chat = useChat(SIDEBAR, 'CBT 治疗对话');

const cbtPrompts = [
  '我最近总是感到焦虑',
  '我想改变我的负面想法',
  '帮我分析这个情境',
  '教我一些放松技巧'
];

// ============ Methods ============

function handleSend(message) {
  chat.sendMessage(message);
}

// ============ Lifecycle ============

onMounted(() => {
  chat.init();
});
</script>

<style scoped>
.cbt-view {
  height: 100vh;
  padding-top: 64px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.cbt-header {
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-primary);
}

.cbt-header h2 {
  margin: 0 0 8px 0;
  color: var(--text-primary);
}

.cbt-header p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.cbt-welcome {
  text-align: center;
  padding: 40px;
}

.welcome-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.cbt-welcome h2 {
  font-size: 28px;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.cbt-welcome > p {
  color: var(--text-secondary);
  margin-bottom: 32px;
}

.cbt-features {
  display: flex;
  justify-content: center;
  gap: 32px;
  margin-bottom: 32px;
}

.feature {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.feature-icon {
  font-size: 32px;
}

.feature span:last-child {
  font-size: 14px;
  color: var(--text-secondary);
}

.quick-starts {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
  max-width: 600px;
  margin: 0 auto;
}

.quick-starts button {
  padding: 10px 20px;
  background: rgba(139, 92, 246, 0.1);
  border: 1px solid rgba(139, 92, 246, 0.2);
  border-radius: 20px;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.quick-starts button:hover {
  background: rgba(139, 92, 246, 0.2);
  border-color: #8b5cf6;
  color: var(--text-primary);
}
</style>
