<template>
  <div class="empathy-view">
    <div class="empathy-header">
      <h2>💙 共情对话</h2>
      <p>一个倾听和理解的温暖空间，提供情感支持</p>
    </div>
    
    <ChatPanel
      :messages="chat.messages.value"
      :is-loading="chat.isLoading.value"
      :error="chat.error.value"
      :sessions="chat.sessions.value"
      :current-session-key="chat.sessionKey.value"
      show-sidebar
      :welcome-title="'共情对话'"
      :welcome-description="'在这里，你可以安全地表达任何感受，我会倾听并提供支持'"
      :placeholder="'分享你的感受...'"
      @send="handleSend"
      @new-chat="chat.createNewSession"
      @select-session="chat.loadSession"
      @delete-session="chat.deleteSession"
    >
      <template #welcome>
        <div class="empathy-welcome">
          <div class="welcome-icon">💙</div>
          <h2>共情对话</h2>
          <p>我在这里倾听你，无论你想说什么</p>
          
          <div class="empathy-pillars">
            <div class="pillar">
              <span>👂 倾听</span>
            </div>
            <div class="pillar">
              <span>💙 理解</span>
            </div>
            <div class="pillar">
              <span>🤝 支持</span>
            </div>
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
const SIDEBAR = 'empathy'; // 独立的 sidebar

const chat = useChat(SIDEBAR, '共情对话');

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
.empathy-view {
  height: 100vh;
  padding-top: 64px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.empathy-header {
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-primary);
}

.empathy-header h2 {
  margin: 0 0 8px 0;
  color: var(--text-primary);
}

.empathy-header p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.empathy-welcome {
  text-align: center;
  padding: 40px;
}

.welcome-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.empathy-welcome h2 {
  font-size: 28px;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.empathy-welcome > p {
  color: var(--text-secondary);
  margin-bottom: 32px;
}

.empathy-pillars {
  display: flex;
  justify-content: center;
  gap: 24px;
}

.pillar {
  padding: 16px 32px;
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 12px;
  font-size: 16px;
  color: var(--text-secondary);
}
</style>
