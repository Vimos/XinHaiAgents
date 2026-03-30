<template>
  <div class="chat-view">
    <ChatPanel
      :messages="chat.messages.value"
      :is-loading="chat.isLoading.value"
      :error="chat.error.value"
      :sessions="chat.sessions.value"
      :current-session-key="chat.sessionKey.value"
      show-sidebar
      :welcome-title="'AI 对话助手'"
      :welcome-description="'我是你的 AI 助手，可以回答问题、协助创作、分析数据等'"
      @send="handleSend"
      @new-chat="chat.createNewSession"
      @select-session="chat.loadSession"
      @delete-session="chat.deleteSession"
    >
      <template #welcome>
        <div class="custom-welcome">
          <div class="welcome-icon">🤖</div>
          <h2>AI 对话助手</h2>
          <p>开始一段新的对话，或从左侧选择历史记录</p>
          
          <div class="quick-starts">
            <button 
              v-for="prompt in quickPrompts" 
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
const SIDEBAR = 'chat'; // 每个页面独立的 sidebar 标识

const chat = useChat(SIDEBAR, 'AI 对话');

const quickPrompts = [
  '帮我写一段 Python 代码',
  '解释一下量子力学',
  '给我讲个笑话',
  '推荐几本好书'
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
.chat-view {
  height: 100vh;
  padding-top: 64px; /* 为导航栏留空间 */
  box-sizing: border-box;
}

.custom-welcome {
  text-align: center;
  padding: 40px;
}

.welcome-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.custom-welcome h2 {
  font-size: 28px;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.custom-welcome p {
  color: var(--text-secondary);
  margin-bottom: 32px;
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
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 20px;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.quick-starts button:hover {
  background: rgba(0, 212, 255, 0.2);
  border-color: var(--accent-primary);
  color: var(--text-primary);
}
</style>
