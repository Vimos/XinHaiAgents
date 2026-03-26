<template>
  <div class="chat-view">
    <!-- Header -->
    <header class="chat-header">
      <div class="chat-header__info">
        <xh-avatar 
          name="XinHai" 
          :is-active="true"
          size="sm"
        />
        <div class="chat-header__title">
          <h3>心海对话</h3>
          <span class="chat-header__status">在线</span>
        </div>
      </div>
      
      <div class="chat-header__actions">
        <xh-button variant="ghost" size="sm" @click="showHistory = true">
          📚 历史记录
        </xh-button>
        <xh-button variant="ghost" size="sm" @click="clearChat">
          🗑️ 清空
        </xh-button>
      </div>
    </header>
    
    <!-- Messages Area -->
    <div ref="messagesContainer" class="chat-messages">
      <!-- Welcome Message -->
      <div v-if="messages.length === 0" class="welcome-message">
        <div class="welcome-icon">🌊</div>
        <h2>欢迎来到心海</h2>
        <p>我是您的AI心理咨询助手，可以为您提供情感支持和专业建议。</p>
        <div class="session-info" v-if="sessionId">
          <span class="session-tag">会话 ID: {{ sessionId.substring(0, 16) }}...</span>
        </div>
        <div class="quick-starters">
          <button
            v-for="starter in quickStarters"
            :key="starter"
            class="starter-btn"
            @click="sendQuickStart(starter)"
          >
            {{ starter }}
          </button>
        </div>
      </div>
      
      <!-- Message List -->
      <div
        v-for="(message, index) in messages"
        :key="index"
        :class="['message', `message--${message.role}`]"
      >
        <xh-avatar
          :name="message.role === 'user' ? '用户' : '心海'"
          size="md"
        />
        
        <div class="message__content">
          <!-- Image Preview -->
          <div v-if="message.image" class="message__image">
            <img :src="message.image" alt="Uploaded image" />
          </div>
          
          <!-- Text Content -->
          <div class="message__text" v-html="formatContent(message.content)"></div>
          
          <!-- Timestamp -->
          <span class="message__time">{{ formatTime(message.timestamp) }}</span>
        </div>
      </div>
      
      <!-- Loading Indicator -->
      <div v-if="isLoading" class="message message--assistant">
        <xh-avatar name="心海" size="md" :is-thinking="true" />
        <div class="message__content">
          <div class="typing-indicator">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- History Modal -->
    <div v-if="showHistory" class="history-modal" @click.self="showHistory = false">
      <div class="history-panel">
        <div class="history-header">
          <h3>📚 历史会话</h3>
          <button class="close-btn" @click="showHistory = false">✕</button>
        </div>
        
        <div class="history-list">
          <div v-if="sessions.length === 0" class="empty-history">
            暂无历史记录
          </div>
          
          <div
            v-for="session in sessions"
            :key="session.sessionId"
            :class="['history-item', { active: session.sessionId === sessionId }]"
            @click="loadSession(session.sessionId)"
          >
            <div class="history-title">{{ session.title }}</div>
            <div class="history-meta">
              <span>{{ session.messageCount }} 条消息</span>
              <span>{{ formatDate(session.timestamp) }}</span>
            </div>
            
            <button 
              class="delete-btn" 
              @click.stop="deleteSession(session.sessionId)"
            >
              🗑️
            </button>
          </div>
        </div>
        
        <div class="history-actions">
          <xh-button variant="primary" @click="createNewSession">
            + 新建对话
          </xh-button>
        </div>
      </div>
    </div>
    
    <!-- Input Area -->
    <div class="chat-input-area">
      <!-- Image Preview -->
      <div v-if="selectedImage" class="image-preview">
        <img :src="selectedImage" alt="Selected" />
        <button class="image-preview__remove" @click="removeImage">×</button>
      </div>
      
      <div class="input-wrapper">
        <input
          ref="fileInput"
          type="file"
          accept="image/*"
          style="display: none"
          @change="handleFileSelect"
        />
        
        <button
          class="input-action"
          :class="{ 'input-action--active': selectedImage }"
          @click="$refs.fileInput.click()"
        >
          📷
        </button>
        
        <textarea
          v-model="inputMessage"
          class="chat-input"
          placeholder="输入消息..."
          rows="1"
          @keydown.enter.prevent="handleEnter"
          @input="autoResize"
        ></textarea>
        
        <xh-button
          variant="primary"
          size="sm"
          :loading="isLoading"
          :disabled="!canSend"
          @click="sendMessage"
        >
          发送
        </xh-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, watch, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { chatApi } from '@/api/chat.js';
import { 
  generateSessionId, 
  saveChatHistory, 
  loadChatHistory, 
  deleteChatHistory,
  getAllSessions 
} from '@/utils/storage.js';
import XhAvatar from '@/components/ui/XhAvatar.vue';
import XhButton from '@/components/ui/XhButton.vue';

const route = useRoute();
const router = useRouter();

// State
const sessionId = ref('');
const messages = ref([]);
const inputMessage = ref('');
const selectedImage = ref(null);
const isLoading = ref(false);
const messagesContainer = ref(null);
const fileInput = ref(null);
const showHistory = ref(false);
const sessions = ref([]);

// Quick starter messages
const quickStarters = [
  '我最近感到很焦虑',
  '如何改善睡眠质量？',
  '工作中压力很大怎么办？',
  '如何与他人更好地沟通？'
];

// Computed
const canSend = computed(() => {
  return (inputMessage.value.trim() || selectedImage.value) && !isLoading.value;
});

// Load sessions list
const loadSessionsList = () => {
  sessions.value = getAllSessions();
};

// Create new session
const createNewSession = () => {
  sessionId.value = generateSessionId();
  messages.value = [];
  saveChatHistory(sessionId.value, []);
  loadSessionsList();
  showHistory.value = false;
  
  // Update URL
  router.replace({ query: { ...route.query, session: sessionId.value } });
};

// Load specific session
const loadSession = (id) => {
  const history = loadChatHistory(id);
  if (history) {
    sessionId.value = id;
    messages.value = history;
    showHistory.value = false;
    
    // Update URL
    router.replace({ query: { ...route.query, session: id } });
  }
};

// Delete session
const deleteSession = (id) => {
  if (confirm('确定要删除这个会话吗？')) {
    deleteChatHistory(id);
    loadSessionsList();
    
    // If current session deleted, create new one
    if (id === sessionId.value) {
      createNewSession();
    }
  }
};

// Initialize
onMounted(() => {
  loadSessionsList();
  
  // Check for session in URL
  const urlSessionId = route.query.session;
  if (urlSessionId) {
    const history = loadChatHistory(urlSessionId);
    if (history) {
      sessionId.value = urlSessionId;
      messages.value = history;
      return;
    }
  }
  
  // Try to load most recent session
  const recentSessions = getAllSessions();
  if (recentSessions.length > 0) {
    const mostRecent = recentSessions[0];
    loadSession(mostRecent.sessionId);
  } else {
    // Create new session
    createNewSession();
  }
});

// Watch messages and save to storage
watch(messages, () => {
  scrollToBottom();
  
  // Auto save (debounced)
  if (sessionId.value) {
    saveChatHistory(sessionId.value, messages.value);
    loadSessionsList();
  }
}, { deep: true });

// Methods
function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
}

function autoResize(e) {
  const textarea = e.target;
  textarea.style.height = 'auto';
  textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
}

function handleEnter(e) {
  if (!e.shiftKey) {
    sendMessage();
  }
}

async function handleFileSelect(e) {
  const file = e.target.files[0];
  if (!file) return;
  
  // Convert to base64
  const reader = new FileReader();
  reader.onload = (event) => {
    selectedImage.value = event.target.result;
  };
  reader.readAsDataURL(file);
}

function removeImage() {
  selectedImage.value = null;
  if (fileInput.value) {
    fileInput.value.value = '';
  }
}

async function sendQuickStart(text) {
  inputMessage.value = text;
  await sendMessage();
}

async function sendMessage() {
  if (!canSend.value) return;
  
  const userMessage = inputMessage.value.trim();
  const imageToSend = selectedImage.value;
  
  // Add user message to UI
  messages.value.push({
    role: 'user',
    content: userMessage,
    image: imageToSend,
    timestamp: Date.now()
  });
  
  // Clear input
  inputMessage.value = '';
  selectedImage.value = null;
  if (fileInput.value) {
    fileInput.value.value = '';
  }
  
  // Reset textarea height
  nextTick(() => {
    const textarea = document.querySelector('.chat-input');
    if (textarea) textarea.style.height = 'auto';
  });
  
  // Show loading
  isLoading.value = true;
  
  try {
    // Use streaming API
    await chatApi.sendMessageStream(
      userMessage,
      imageToSend,
      (delta, fullContent) => {
        // Update or create assistant message
        const lastMessage = messages.value[messages.value.length - 1];
        if (lastMessage.role === 'assistant') {
          lastMessage.content = fullContent;
        } else {
          messages.value.push({
            role: 'assistant',
            content: fullContent,
            timestamp: Date.now()
          });
        }
      },
      '你是心海(XinHai)，一位专业的心理咨询助手。你具备丰富的心理学知识，包括CBT、情感支持、危机干预等专业技能。你的回复应该专业、有同理心、富有洞察力。'
    );
    
  } catch (error) {
    console.error('Send message error:', error);
    messages.value.push({
      role: 'assistant',
      content: '抱歉，我遇到了一些问题。请稍后再试。',
      timestamp: Date.now()
    });
  } finally {
    isLoading.value = false;
  }
}

function clearChat() {
  if (confirm('确定要清空当前对话吗？')) {
    messages.value = [];
    if (sessionId.value) {
      saveChatHistory(sessionId.value, []);
      loadSessionsList();
    }
  }
}

function formatContent(content) {
  // Simple markdown-like formatting
  return content
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>');
}

function formatTime(timestamp) {
  const date = new Date(timestamp);
  return date.toLocaleTimeString('zh-CN', { 
    hour: '2-digit', 
    minute: '2-digit' 
  });
}

function formatDate(timestamp) {
  const date = new Date(timestamp);
  return date.toLocaleDateString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}
</script>

<style scoped>
.chat-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: rgba(10, 22, 40, 0.6);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

/* Header */
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-md) var(--space-lg);
  background: rgba(0, 0, 0, 0.2);
  border-bottom: 1px solid rgba(0, 212, 255, 0.1);
}

.chat-header__info {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.chat-header__title h3 {
  margin: 0;
  font-size: var(--text-lg);
  color: var(--text-primary);
}

.chat-header__status {
  font-size: var(--text-xs);
  color: var(--accent-success);
}

.chat-header__status::before {
  content: '';
  display: inline-block;
  width: 6px;
  height: 6px;
  background: var(--accent-success);
  border-radius: 50%;
  margin-right: 4px;
  animation: pulse-glow 2s ease-in-out infinite;
}

.chat-header__actions {
  display: flex;
  gap: var(--space-sm);
}

/* Messages Area */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-lg);
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

/* Welcome Message */
.welcome-message {
  text-align: center;
  padding: var(--space-3xl);
  margin: auto;
}

.welcome-icon {
  font-size: 64px;
  margin-bottom: var(--space-lg);
  animation: float 3s ease-in-out infinite;
}

.welcome-message h2 {
  font-size: var(--text-2xl);
  color: var(--text-primary);
  margin-bottom: var(--space-md);
}

.welcome-message p {
  color: var(--text-secondary);
  margin-bottom: var(--space-md);
}

.session-info {
  margin-bottom: var(--space-lg);
}

.session-tag {
  font-size: var(--text-xs);
  color: var(--text-muted);
  background: rgba(0, 212, 255, 0.1);
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-sm);
}

.quick-starters {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-md);
  justify-content: center;
  margin-top: var(--space-xl);
}

.starter-btn {
  padding: var(--space-sm) var(--space-md);
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.starter-btn:hover {
  background: rgba(0, 212, 255, 0.2);
  border-color: var(--accent-primary);
  color: var(--text-primary);
}

/* History Modal */
.history-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.history-panel {
  width: 400px;
  max-width: 90%;
  max-height: 70%;
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-md) var(--space-lg);
  border-bottom: 1px solid var(--border-color);
}

.history-header h3 {
  margin: 0;
  color: var(--text-primary);
}

.close-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 20px;
  cursor: pointer;
  padding: var(--space-xs);
}

.close-btn:hover {
  color: var(--text-primary);
}

.history-list {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-md);
}

.empty-history {
  text-align: center;
  color: var(--text-muted);
  padding: var(--space-xl);
}

.history-item {
  position: relative;
  padding: var(--space-md);
  background: rgba(0, 0, 0, 0.2);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
  border: 1px solid transparent;
}

.history-item:hover {
  background: rgba(0, 212, 255, 0.1);
  border-color: var(--accent-primary);
}

.history-item.active {
  background: rgba(0, 212, 255, 0.15);
  border-color: var(--accent-primary);
}

.history-title {
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--space-xs);
  padding-right: 30px;
}

.history-meta {
  display: flex;
  gap: var(--space-md);
  font-size: var(--text-xs);
  color: var(--text-muted);
}

.delete-btn {
  position: absolute;
  top: var(--space-sm);
  right: var(--space-sm);
  background: none;
  border: none;
  cursor: pointer;
  opacity: 0.5;
  transition: opacity var(--transition-fast);
}

.delete-btn:hover {
  opacity: 1;
}

.history-actions {
  padding: var(--space-md);
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: center;
}

/* Message Bubbles */
.message {
  display: flex;
  gap: var(--space-md);
  max-width: 80%;
  animation: message-appear 0.3s ease-out forwards;
}

.message--user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message--assistant {
  align-self: flex-start;
}

.message__content {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
  padding: var(--space-md);
  border-radius: var(--radius-lg);
  background: var(--bg-secondary);
}

.message--user .message__content {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.15) 0%, rgba(159, 122, 234, 0.15) 100%);
  border: 1px solid rgba(0, 212, 255, 0.2);
}

.message__image {
  max-width: 200px;
  border-radius: var(--radius-md);
  overflow: hidden;
}

.message__image img {
  width: 100%;
  height: auto;
  display: block;
}

.message__text {
  color: var(--text-primary);
  line-height: 1.6;
  word-wrap: break-word;
}

.message__time {
  font-size: var(--text-xs);
  color: var(--text-muted);
  align-self: flex-end;
}

/* Typing Indicator */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: var(--space-sm);
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
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.4;
  }
  30% {
    transform: translateY(-10px);
    opacity: 1;
  }
}

/* Input Area */
.chat-input-area {
  padding: var(--space-md) var(--space-lg);
  background: rgba(0, 0, 0, 0.2);
  border-top: 1px solid rgba(0, 212, 255, 0.1);
}

.image-preview {
  position: relative;
  display: inline-block;
  margin-bottom: var(--space-sm);
}

.image-preview img {
  max-width: 100px;
  max-height: 100px;
  border-radius: var(--radius-md);
}

.image-preview__remove {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 20px;
  height: 20px;
  background: var(--accent-danger);
  border: none;
  border-radius: 50%;
  color: white;
  cursor: pointer;
  font-size: 12px;
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: var(--space-md);
  background: var(--bg-secondary);
  padding: var(--space-sm);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
}

.input-wrapper:focus-within {
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.15);
}

.input-action {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  font-size: 20px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.input-action:hover {
  background: rgba(0, 212, 255, 0.1);
}

.input-action--active {
  background: rgba(0, 212, 255, 0.2);
}

.chat-input {
  flex: 1;
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-size: var(--text-base);
  font-family: var(--font-family);
  resize: none;
  outline: none;
  line-height: 1.5;
  max-height: 120px;
  min-height: 24px;
}

.chat-input::placeholder {
  color: var(--text-muted);
}

/* Animations */
@keyframes message-appear {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 0 5px var(--accent-success);
  }
  50% {
    box-shadow: 0 0 15px var(--accent-success);
  }
}
</style>
