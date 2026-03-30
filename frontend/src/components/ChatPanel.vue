<template>
  <div class="chat-panel">
    <!-- 历史会话侧边栏 -->
    <div v-if="showSidebar" class="chat-sidebar">
      <div class="sidebar-header">
        <button class="new-chat-btn" @click="onNewChat">
          <span>+</span> 新对话
        </button>
      </div>
      
      <div class="sessions-list">
        <div
          v-for="session in sessions"
          :key="session.sessionKey"
          :class="['session-item', { active: session.sessionKey === currentSessionKey }]"
          @click="onSelectSession(session.sessionKey)"
        >
          <span class="session-title">{{ session.title || '未命名对话' }}</span>
          <span class="session-count">{{ session.messageCount || 0 }} 条</span>
          <button 
            class="delete-btn" 
            @click.stop="onDeleteSession(session.sessionKey)"
          >
            ×
          </button>
        </div>
        
        <div v-if="sessions.length === 0" class="empty-sessions">
          暂无历史对话
        </div>
      </div>
    </div>
    
    <!-- 主对话区域 -->
    <div class="chat-main">
      <!-- 消息列表 -->
      <div ref="messagesContainer" class="messages-list">
        <div v-if="!hasMessages" class="welcome-area">
          <slot name="welcome">
            <div class="default-welcome">
              <h3>{{ welcomeTitle }}</h3>
              <p>{{ welcomeDescription }}</p>
            </div>
          </slot>
        </div>
        
        <template v-else>
          <div
            v-for="(msg, index) in messages"
            :key="index"
            :class="['message', `message--${msg.role}`]"
          >
            <div class="message-avatar">
              {{ msg.role === 'user' ? '👤' : '🤖' }}
            </div>
            
            <div class="message-content">
              <div class="message-header">
                <span class="message-role">{{ msg.role === 'user' ? '我' : 'AI' }}</span>
                <span class="message-time">{{ formatTime(msg.timestamp) }}</span>
              </div>
              
              <div class="message-body" v-html="formatMarkdown(msg.content)"></div>
            </div>
          </div>
          
          <!-- 加载中指示器 -->
          <div v-if="isLoading && !lastMessage?.content" class="message message--assistant">
            <div class="message-avatar">🤖</div>
            <div class="message-content">
              <div class="typing-indicator">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
        </template>
      </div>
      
      <!-- 输入区域 -->
      <div class="input-area">
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        
        <div class="input-wrapper">
          <textarea
            v-model="inputMessage"
            :disabled="isLoading"
            :placeholder="placeholder"
            rows="1"
            @keydown.enter.prevent="handleSend"
            @input="autoResize"
            ref="textareaRef"
          ></textarea>
          
          <button
            class="send-btn"
            :disabled="!inputMessage.trim() || isLoading"
            @click="handleSend"
          >
            {{ isLoading ? '...' : '发送' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue';
import { marked } from 'marked';

const props = defineProps({
  // 对话状态
  messages: { type: Array, default: () => [] },
  isLoading: { type: Boolean, default: false },
  error: { type: String, default: null },
  
  // 会话列表
  sessions: { type: Array, default: () => [] },
  currentSessionKey: { type: String, default: '' },
  
  // UI 配置
  showSidebar: { type: Boolean, default: true },
  welcomeTitle: { type: String, default: '开始对话' },
  welcomeDescription: { type: String, default: '输入消息开始与 AI 对话' },
  placeholder: { type: String, default: '输入消息...' }
});

const emit = defineEmits([
  'send', 'new-chat', 'select-session', 'delete-session'
]);

const inputMessage = ref('');
const messagesContainer = ref(null);
const textareaRef = ref(null);

// ============ Methods ============

function handleSend() {
  if (!inputMessage.value.trim() || props.isLoading) return;
  
  emit('send', inputMessage.value.trim());
  inputMessage.value = '';
  
  // 重置文本框高度
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto';
  }
}

function onNewChat() {
  emit('new-chat');
}

function onSelectSession(sessionKey) {
  emit('select-session', sessionKey);
}

function onDeleteSession(sessionKey) {
  if (confirm('确定要删除这个对话吗？')) {
    emit('delete-session', sessionKey);
  }
}

function autoResize(e) {
  const textarea = e.target;
  textarea.style.height = 'auto';
  textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
}

function formatMarkdown(content) {
  if (!content) return '';
  try {
    return marked.parse(content, { breaks: true });
  } catch (e) {
    return content.replace(/\n/g, '<br>');
  }
}

function formatTime(timestamp) {
  if (!timestamp) return '';
  const date = new Date(timestamp);
  return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
}

// 自动滚动到底部
watch(() => props.messages, () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
}, { deep: true });
</script>

<style scoped>
.chat-panel {
  display: flex;
  height: 100%;
  background: var(--bg-secondary);
}

/* 侧边栏 */
.chat-sidebar {
  width: 260px;
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
}

.new-chat-btn {
  width: 100%;
  padding: 10px;
  background: var(--accent-primary);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.new-chat-btn:hover {
  opacity: 0.9;
}

.sessions-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.session-item {
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background 0.2s;
}

.session-item:hover {
  background: rgba(0, 212, 255, 0.1);
}

.session-item.active {
  background: rgba(0, 212, 255, 0.15);
  border: 1px solid rgba(0, 212, 255, 0.3);
}

.session-title {
  flex: 1;
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.session-count {
  font-size: 12px;
  color: var(--text-muted);
}

.delete-btn {
  width: 20px;
  height: 20px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.session-item:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  background: rgba(255, 0, 0, 0.2);
  color: red;
}

.empty-sessions {
  padding: 32px;
  text-align: center;
  color: var(--text-muted);
  font-size: 14px;
}

/* 主区域 */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.messages-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.welcome-area {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.default-welcome {
  text-align: center;
  color: var(--text-secondary);
}

.default-welcome h3 {
  font-size: 24px;
  margin-bottom: 12px;
  color: var(--text-primary);
}

/* 消息样式 */
.message {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  font-size: 18px;
  flex-shrink: 0;
}

.message--user .message-avatar {
  background: var(--accent-primary);
}

.message-content {
  flex: 1;
  max-width: calc(100% - 60px);
}

.message-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 4px;
}

.message-role {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 14px;
}

.message-time {
  font-size: 12px;
  color: var(--text-muted);
}

.message-body {
  color: var(--text-secondary);
  line-height: 1.6;
  font-size: 14px;
}

.message-body :deep(p) {
  margin: 8px 0;
}

.message-body :deep(pre) {
  background: var(--bg-tertiary);
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
}

.message-body :deep(code) {
  background: var(--bg-tertiary);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
}

/* 输入区域 */
.input-area {
  border-top: 1px solid var(--border-color);
  padding: 16px 20px;
  background: var(--bg-primary);
}

.error-message {
  color: #ff4444;
  font-size: 14px;
  margin-bottom: 8px;
  padding: 8px 12px;
  background: rgba(255, 68, 68, 0.1);
  border-radius: 6px;
}

.input-wrapper {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.input-wrapper textarea {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 14px;
  resize: none;
  line-height: 1.5;
  max-height: 120px;
}

.input-wrapper textarea:focus {
  outline: none;
  border-color: var(--accent-primary);
}

.input-wrapper textarea:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.send-btn {
  padding: 12px 24px;
  background: var(--accent-primary);
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-size: 14px;
  transition: opacity 0.2s;
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-btn:not(:disabled):hover {
  opacity: 0.9;
}

/* 打字动画 */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 8px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: var(--accent-primary);
  border-radius: 50%;
  animation: typing 1.4s ease-in-out infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-10px); }
}
</style>
