<template>
  <div class="chat-view">
    <!-- Header -->
    <header class="chat-header">
      <div class="chat-header__info">
        <xh-avatar :name="assistantName" :is-active="true" size="sm" />
        <div class="chat-header__title">
          <h3>{{ title }}</h3>
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
        <div class="welcome-icon">{{ icon }}</div>
        <h2>{{ welcomeTitle }}</h2>
        <p>{{ welcomeDescription }}</p>
        <div class="session-info" v-if="sessionId">
          <span class="session-tag">会话: {{ sessionId.substring(0, 20) }}...</span>
        </div>
        
        <div class="quick-starters" v-if="quickStarters.length">
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
          :name="message.role === 'user' ? '用户' : assistantName"
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
        <xh-avatar :name="assistantName" size="md" :is-thinking="true" />
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
          <h3>📚 {{ title }} - 历史会话</h3>
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
import axios from 'axios';
import XhAvatar from '@/components/ui/XhAvatar.vue';
import XhButton from '@/components/ui/XhButton.vue';
import { 
  generateSessionId, 
  saveChatHistory, 
  loadChatHistory, 
  deleteChatHistory,
  getSessionsBySidebar,
  getMostRecentSession
} from '@/utils/storage.js';

// Props for customization
const props = defineProps({
  sidebar: {
    type: String,
    default: 'chat'
  },
  title: {
    type: String,
    default: '心海对话'
  },
  assistantName: {
    type: String,
    default: '心海'
  },
  icon: {
    type: String,
    default: '🌊'
  },
  welcomeTitle: {
    type: String,
    default: '欢迎来到心海'
  },
  welcomeDescription: {
    type: String,
    default: '我是您的AI心理咨询助手，可以为您提供情感支持和专业建议。'
  },
  systemPrompt: {
    type: String,
    default: '你是心海(XinHai)，一位专业的心理咨询助手。'
  },
  quickStarters: {
    type: Array,
    default: () => [
      '我最近感到很焦虑',
      '如何改善睡眠质量？',
      '工作中压力很大怎么办？',
      '如何与他人更好地沟通？'
    ]
  }
});

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

// API 配置
const API_URL = '/openclaw';
const API_TOKEN = process.env.VUE_APP_OPENCLAW_TOKEN 
  || process.env.VITE_OPENCLAW_TOKEN 
  || '';

const api = axios.create({
  baseURL: API_URL,
  timeout: 300000,
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${API_TOKEN}`
  },
});

// Computed
const canSend = computed(() => {
  return (inputMessage.value.trim() || selectedImage.value) && !isLoading.value;
});

// Load sessions list for current sidebar
const loadSessionsList = () => {
  sessions.value = getSessionsBySidebar(props.sidebar);
};

// Create new session for current sidebar
const createNewSession = () => {
  sessionId.value = generateSessionId(props.sidebar);
  messages.value = [];
  saveChatHistory(sessionId.value, props.sidebar, []);
  loadSessionsList();
  showHistory.value = false;
  
  // Update URL
  router.replace({ 
    path: route.path, 
    query: { ...route.query, session: sessionId.value } 
  });
};

// Load specific session
const loadSession = (id) => {
  const history = loadChatHistory(id);
  if (history && history.sidebar === props.sidebar) {
    sessionId.value = id;
    messages.value = history.messages || [];
    showHistory.value = false;
    
    // Update URL
    router.replace({ 
      path: route.path, 
      query: { ...route.query, session: id } 
    });
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
    // Only load if it belongs to current sidebar
    if (history && history.sidebar === props.sidebar) {
      sessionId.value = urlSessionId;
      messages.value = history.messages || [];
      return;
    }
  }
  
  // Try to load most recent session for this sidebar
  const recentSessionId = getMostRecentSession(props.sidebar);
  if (recentSessionId) {
    const history = loadChatHistory(recentSessionId);
    if (history) {
      sessionId.value = recentSessionId;
      messages.value = history.messages || [];
      return;
    }
  }
  
  // Create new session for this sidebar
  createNewSession();
});

// Watch messages and save to storage
watch(messages, () => {
  scrollToBottom();
  
  // Auto save (debounced)
  if (sessionId.value) {
    saveChatHistory(sessionId.value, props.sidebar, messages.value);
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
    // Build messages array
    const apiMessages = [
      { role: 'system', content: props.systemPrompt }
    ];
    
    if (imageToSend && imageToSend.startsWith('data:image')) {
      apiMessages.push({
        role: 'user',
        content: [
          { type: 'text', text: userMessage },
          { type: 'image_url', image_url: { url: imageToSend } }
        ]
      });
    } else {
      apiMessages.push({ role: 'user', content: userMessage });
    }
    
    let content = '';
    
    await api.post('/v1/chat/completions', {
      model: 'openclaw:main',
      messages: apiMessages,
      temperature: 0.7,
      max_tokens: 2000,
      stream: true,
      user: sessionId.value  // 使用前端 sessionId 作为后端 sessionKey
    }, {
      responseType: 'text',
      onDownloadProgress: (progressEvent) => {
        const text = progressEvent.event.target.responseText;
        if (!text) return;
        
        const lines = text.split('\n').filter(line => line.trim());
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') continue;
            
            try {
              const json = JSON.parse(data);
              const delta = json.choices?.[0]?.delta?.content;
              if (delta) {
                content += delta;
                
                const lastMessage = messages.value[messages.value.length - 1];
                if (lastMessage.role === 'assistant') {
                  lastMessage.content = content;
                } else {
                  messages.value.push({
                    role: 'assistant',
                    content: content,
                    timestamp: Date.now()
                  });
                }
              }
            } catch (e) {
              // Ignore parse errors for incomplete JSON chunks
            }
          }
        }
      }
    });
    
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
      saveChatHistory(sessionId.value, props.sidebar, []);
      loadSessionsList();
    }
  }
}

function formatContent(content) {
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
/* 样式与 ChatView.vue 相同，省略... */
.chat-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: rgba(10, 22, 40, 0.6);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

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

@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 5px var(--accent-success); }
  50% { box-shadow: 0 0 15px var(--accent-success); }
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-lg);
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

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

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
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
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-10px); opacity: 1; }
}

@keyframes message-appear {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
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
</style>
