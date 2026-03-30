/**
 * useChat - 对话逻辑组合式函数
 * 每个页面独立实例，管理自己的对话状态
 */
import { ref, computed } from 'vue';
import { chatApi } from '@/api/index.js';
import { marked } from 'marked';

export function useChat(sidebar, title = '新对话') {
  // ============ State ============
  const sessionKey = ref(generateSessionKey());
  const messages = ref([]);
  const isLoading = ref(false);
  const error = ref(null);
  const sessions = ref([]); // 该 sidebar 的历史会话列表

  // ============ Getters ============
  const hasMessages = computed(() => messages.value.length > 0);
  const lastMessage = computed(() => messages.value[messages.value.length - 1]);

  // ============ Actions ============

  /**
   * 生成会话 key
   */
  function generateSessionKey() {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * 加载会话列表
   */
  async function loadSessions() {
    try {
      const data = await chatApi.getHistory(sidebar);
      sessions.value = data.sessions || [];
      return sessions.value;
    } catch (e) {
      console.error('加载会话列表失败:', e);
      return [];
    }
  }

  /**
   * 加载指定会话
   */
  async function loadSession(key) {
    try {
      const data = await chatApi.getSession(key);
      sessionKey.value = data.sessionKey;
      messages.value = data.messages || [];
      return data;
    } catch (e) {
      console.error('加载会话失败:', e);
      error.value = e.message;
      throw e;
    }
  }

  /**
   * 创建新会话
   */
  function createNewSession() {
    sessionKey.value = generateSessionKey();
    messages.value = [];
    error.value = null;
  }

  /**
   * 保存当前会话到后端
   */
  async function saveSession() {
    if (!hasMessages.value) return;
    
    try {
      await chatApi.saveSession({
        sessionKey: sessionKey.value,
        sidebar,
        title,
        messages: messages.value
      });
      // 保存成功后刷新会话列表
      await loadSessions();
    } catch (e) {
      console.error('保存会话失败:', e);
    }
  }

  /**
   * 删除会话
   */
  async function deleteSession(key) {
    try {
      await chatApi.deleteSession(key);
      // 如果删除的是当前会话，创建新会话
      if (key === sessionKey.value) {
        createNewSession();
      }
      await loadSessions();
    } catch (e) {
      console.error('删除会话失败:', e);
    }
  }

  /**
   * 发送消息（核心方法）
   */
  async function sendMessage(content) {
    if (!content.trim() || isLoading.value) return;

    // 添加用户消息
    messages.value.push({
      role: 'user',
      content: content.trim(),
      timestamp: Date.now()
    });

    isLoading.value = true;
    error.value = null;

    // 准备 AI 消息占位
    const aiMessageIndex = messages.value.length;
    messages.value.push({
      role: 'assistant',
      content: '',
      timestamp: Date.now()
    });

    try {
      await chatApi.sendMessage({
        messages: messages.value.slice(0, -1).map(m => ({
          role: m.role,
          content: m.content
        })),
        sidebar,
        sessionKey: sessionKey.value,
        onChunk: (fullContent, _delta) => {
          // 实时更新 AI 消息 (fullContent 包含完整内容)
          messages.value[aiMessageIndex].content = fullContent;
        },
        onError: (err) => {
          error.value = err.message;
          messages.value[aiMessageIndex].content = '抱歉，发生了错误，请重试。';
        },
        onComplete: () => {
          // 完成后保存到后端
          saveSession();
        }
      });
    } catch (e) {
      console.error('发送消息失败:', e);
      error.value = e.message;
      messages.value[aiMessageIndex].content = '抱歉，发生了错误，请重试。';
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * 格式化 Markdown
   */
  function formatMarkdown(content) {
    if (!content) return '';
    try {
      return marked.parse(content, { breaks: true });
    } catch (e) {
      return content.replace(/\n/g, '<br>');
    }
  }

  /**
   * 初始化 - 加载最近会话或创建新会话
   */
  async function init() {
    await loadSessions();
    
    // 如果有历史会话，加载最新的
    if (sessions.value.length > 0) {
      const latest = sessions.value[0];
      await loadSession(latest.sessionKey);
    } else {
      createNewSession();
    }
  }

  return {
    // State
    sessionKey,
    messages,
    isLoading,
    error,
    sessions,
    
    // Getters
    hasMessages,
    lastMessage,
    
    // Actions
    init,
    loadSessions,
    loadSession,
    createNewSession,
    saveSession,
    deleteSession,
    sendMessage,
    formatMarkdown
  };
}
