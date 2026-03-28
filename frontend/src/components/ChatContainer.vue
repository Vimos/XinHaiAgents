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
        <xh-button 
          v-if="toolCalls.length > 0"
          variant="ghost" 
          size="sm" 
          @click="showToolCalls = !showToolCalls"
          :class="{ 'active': showToolCalls }"
        >
          🔧 工具调用 ({{ toolCalls.length }})
        </xh-button>
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
    
    <!-- Tool Calls Panel -->
    <div v-if="showToolCalls && toolCalls.length > 0" class="toolcalls-panel">
      <div class="toolcalls-header">
        <span>🔧 工具调用记录</span>
        <xh-button variant="ghost" size="sm" @click="showToolCalls = false">✕</xh-button>
      </div>
      <div class="toolcalls-list">
        <div 
          v-for="(call, index) in toolCalls" 
          :key="index"
          class="toolcall-item"
        >
          <div class="toolcall-header">
            <span class="toolcall-name">{{ call.name }}</span>
            <span class="toolcall-time">{{ formatTime(call.timestamp) }}</span>
          </div>
          <div class="toolcall-args">
            <pre>{{ JSON.stringify(call.arguments, null, 2) }}</pre>
          </div>
          <div v-if="call.result" class="toolcall-result">
            <div class="result-label">结果:</div>
            <pre>{{ typeof call.result === 'string' ? call.result : JSON.stringify(call.result, null, 2) }}</pre>
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
import { api } from '@/api/chat.js';
import { marked } from 'marked';
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
const toolCalls = ref([]); // 存储 tool call 历史
const showToolCalls = ref(false); // 是否展开 tool call 面板
const inputMessage = ref('');
const selectedImage = ref(null);
const isLoading = ref(false);
const messagesContainer = ref(null);
const fileInput = ref(null);
const showHistory = ref(false);
const sessions = ref([]);

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

// Initialize - 优先从后端加载
onMounted(async () => {
  loadSessionsList();
  
  const token = localStorage.getItem('token');
  
  // 尝试从后端加载会话列表
  if (token) {
    try {
      const res = await fetch(`https://chat.xinhai.co/api/chat/history?sidebar=${props.sidebar}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (res.ok) {
        const data = await res.json();
        
        // 找到当前 sidebar 的会话
        const sidebarSession = data.sessions.find(s => 
          s.sessionKey && s.sessionKey.includes(props.sidebar)
        ) || data.sessions[0];
        
        if (sidebarSession) {
          // 加载该会话的详细内容
          const detailRes = await fetch(
            `https://chat.xinhai.co/api/chat/history/${sidebarSession.sessionKey}`,
            { headers: { 'Authorization': `Bearer ${token}` } }
          );
          
          if (detailRes.ok) {
            const detail = await detailRes.json();
            sessionId.value = detail.sessionKey;
            messages.value = detail.messages || [];
            
            // 同时保存到 localStorage 做缓存
            saveChatHistory(sessionId.value, props.sidebar, messages.value);
            return;
          }
        }
      }
    } catch (e) {
      console.error('Failed to load from backend:', e);
    }
  }
  
  // 后端加载失败，回退到 localStorage
  const urlSessionId = route.query.session;
  if (urlSessionId) {
    const history = loadChatHistory(urlSessionId);
    if (history && history.sidebar === props.sidebar) {
      sessionId.value = urlSessionId;
      messages.value = history.messages || [];
      return;
    }
  }
  
  const recentSessionId = getMostRecentSession(props.sidebar);
  if (recentSessionId) {
    const history = loadChatHistory(recentSessionId);
    if (history) {
      sessionId.value = recentSessionId;
      messages.value = history.messages || [];
      return;
    }
  }
  
  // 创建新会话
  createNewSession();
});

// Watch messages and save to storage + backend
watch(messages, async () => {
  scrollToBottom();
  
  // Auto save to localStorage
  if (sessionId.value) {
    saveChatHistory(sessionId.value, props.sidebar, messages.value);
    loadSessionsList();
  }
  
  // Sync to backend API
  if (sessionId.value && messages.value.length > 0) {
    try {
      const token = localStorage.getItem('token');
      if (token) {
        await fetch('https://chat.xinhai.co/api/chat/history', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            session_key: sessionId.value,
            sidebar: props.sidebar,
            title: props.title,
            messages: messages.value
          })
        });
      }
    } catch (e) {
      console.error('Backend save failed:', e);
    }
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

// 保存对话到后端
function saveToBackend() {
  if (!sessionId.value || messages.value.length === 0) return;
  const token = localStorage.getItem('token');
  if (!token) return;
  
  console.log('[ChatContainer] Saving to backend, sidebar:', props.sidebar, 'messages:', messages.value.length);
  
  fetch('https://chat.xinhai.co/api/chat/history', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      session_key: sessionId.value,
      sidebar: props.sidebar,
      title: props.title,
      messages: messages.value
    })
  }).then(res => {
    console.log('[ChatContainer] Backend save response:', res.status);
  }).catch(e => {
    console.error('[ChatContainer] Backend save failed:', e);
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
    let processedLength = 0;  // 记录已处理的数据长度
    let buffer = '';  // 缓冲区，用于处理被分割的数据行
    
    // 使用后端认证服务的 /api/chat/stream 端点
    await api.post('/api/chat/stream', {
      message: userMessage,
      image_base64: imageToSend,
      system_prompt: props.systemPrompt,
      sidebar: props.sidebar
    }, {
      responseType: 'text',
      onDownloadProgress: (progressEvent) => {
        const text = progressEvent.event.target.responseText;
        if (!text || text.length <= processedLength) return;
        
        // 只处理新接收到的数据
        const newText = text.slice(processedLength);
        processedLength = text.length;
        
        // 将新数据追加到缓冲区
        buffer += newText;
        
        // 按行分割，但保留最后一个不完整的行
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';  // 保留不完整的最后一行
        
        for (const line of lines) {
          const trimmedLine = line.trim();
          if (!trimmedLine) continue;
          
          if (trimmedLine.startsWith('data: ')) {
            const data = trimmedLine.slice(6);
            if (data === '[DONE]') continue;
            
            try {
              const json = JSON.parse(data);
              const delta = json.choices?.[0]?.delta;
              
              // 处理 tool_calls
              if (delta?.tool_calls) {
                const toolCall = delta.tool_calls[0];
                if (toolCall?.function) {
                  // 检查是否已存在此 tool call
                  const existingCall = toolCalls.value.find(t => t.index === toolCall.index);
                  if (existingCall) {
                    // 追加参数
                    if (toolCall.function.arguments) {
                      existingCall.arguments += toolCall.function.arguments;
                    }
                  } else {
                    // 新的 tool call
                    toolCalls.value.push({
                      index: toolCall.index,
                      name: toolCall.function.name || 'unknown',
                      arguments: toolCall.function.arguments || '',
                      timestamp: Date.now(),
                      result: null
                    });
                  }
                }
              }
              
              // 处理普通内容
              if (delta?.content) {
                content += delta.content;
                
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
                
                // 自动滚动到底部
                scrollToBottom();
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
    // 直接保存到后端
    saveToBackend();
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

// 配置 marked
marked.setOptions({
  breaks: true,       // 换行符转为 <br>
  gfm: true,          // 支持 GitHub 风格 Markdown
});

function formatContent(content) {
  if (!content) return '';
  try {
    return marked.parse(content);
  } catch (e) {
    // 降级为简单格式化
    return content
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br>');
  }
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

/* Markdown 渲染样式 */
.message__text :deep(h1),
.message__text :deep(h2),
.message__text :deep(h3) {
  margin: 8px 0 4px;
  font-weight: 600;
  color: var(--text-primary);
}

.message__text :deep(h1) { font-size: 1.3em; }
.message__text :deep(h2) { font-size: 1.15em; }
.message__text :deep(h3) { font-size: 1.05em; }

.message__text :deep(p) {
  margin: 4px 0;
}

.message__text :deep(ul),
.message__text :deep(ol) {
  margin: 4px 0;
  padding-left: 20px;
}

.message__text :deep(li) {
  margin: 2px 0;
}

.message__text :deep(code) {
  background: rgba(0, 0, 0, 0.3);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 0.9em;
  color: #e06c75;
}

.message__text :deep(pre) {
  background: rgba(0, 0, 0, 0.4);
  padding: 12px 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 8px 0;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.message__text :deep(pre code) {
  background: none;
  padding: 0;
  color: #abb2bf;
  font-size: 0.85em;
  line-height: 1.5;
}

.message__text :deep(blockquote) {
  border-left: 3px solid rgba(0, 212, 255, 0.5);
  margin: 8px 0;
  padding: 4px 12px;
  color: var(--text-secondary);
  background: rgba(0, 212, 255, 0.05);
  border-radius: 0 4px 4px 0;
}

.message__text :deep(a) {
  color: var(--accent-primary, #00d4ff);
  text-decoration: none;
}

.message__text :deep(a:hover) {
  text-decoration: underline;
}

.message__text :deep(table) {
  border-collapse: collapse;
  margin: 8px 0;
  width: 100%;
}

.message__text :deep(th),
.message__text :deep(td) {
  border: 1px solid rgba(255, 255, 255, 0.15);
  padding: 6px 10px;
  text-align: left;
  font-size: 0.9em;
}

.message__text :deep(th) {
  background: rgba(0, 0, 0, 0.2);
  font-weight: 600;
}

.message__text :deep(hr) {
  border: none;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  margin: 12px 0;
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

/* Tool Calls Panel */
.toolcalls-panel {
  position: fixed;
  right: 20px;
  top: 80px;
  width: 350px;
  max-height: 70vh;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  z-index: 100;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.toolcalls-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-md) var(--space-lg);
  background: rgba(0, 212, 255, 0.1);
  border-bottom: 1px solid var(--border-color);
  font-weight: 600;
  color: var(--text-primary);
}

.toolcalls-list {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-md);
}

.toolcall-item {
  background: rgba(0, 0, 0, 0.2);
  border-radius: var(--radius-md);
  padding: var(--space-md);
  margin-bottom: var(--space-md);
  border: 1px solid rgba(0, 212, 255, 0.2);
}

.toolcall-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-sm);
}

.toolcall-name {
  font-weight: 600;
  color: var(--accent-primary);
  font-size: var(--text-sm);
}

.toolcall-time {
  font-size: var(--text-xs);
  color: var(--text-muted);
}

.toolcall-args pre,
.toolcall-result pre {
  background: rgba(0, 0, 0, 0.3);
  padding: var(--space-sm);
  border-radius: var(--radius-sm);
  font-size: 11px;
  color: var(--text-secondary);
  overflow-x: auto;
  margin: 0;
}

.toolcall-args {
  margin-bottom: var(--space-sm);
}

.toolcall-result {
  border-top: 1px dashed var(--border-color);
  padding-top: var(--space-sm);
}

.result-label {
  font-size: var(--text-xs);
  color: var(--accent-success);
  margin-bottom: var(--space-xs);
}

.chat-header__actions button.active {
  background: rgba(0, 212, 255, 0.2);
  color: var(--accent-primary);
}
</style>
