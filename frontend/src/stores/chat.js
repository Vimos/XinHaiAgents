import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useAuthStore } from './auth';

const API_URL = 'https://chat.xinhai.co';  // 认证服务地址

export const useChatStore = defineStore('chat', () => {
  // ============ State ============
  const sessions = ref([]);  // 会话列表
  const currentSession = ref(null);  // 当前会话
  const messages = ref([]);  // 当前对话消息
  const loading = ref(false);
  
  // ============ Getters ============
  const sessionList = computed(() => sessions.value);
  const currentSessionKey = computed(() => currentSession.value?.sessionKey);
  const hasMessages = computed(() => messages.value.length > 0);
  
  // ============ Actions ============
  
  /**
   * \u767b\u5f55\u540e\u6062\u590d\uff1a\u62c9\u53d6\u7528\u6237\u7684\u6240\u6709会话列表
   */
  async function restoreSessions() {
    const authStore = useAuthStore();
    const token = authStore.token;
    
    if (!token) return;
    
    try {
      const res = await fetch(`${API_URL}/chat/history`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (!res.ok) throw new Error('Failed to load sessions');
      
      const data = await res.json();
      sessions.value = data.sessions;
      
      // \u5982\u679c\u6709\u5386\u53f2会话\uff0c加载\u6700\u8fd1\u7684\u4e00\u4e2a
      if (sessions.value.length > 0) {
        await loadSession(sessions.value[0].sessionKey);
      } else {
        // \u6ca1\u6709\u5386\u53f2\u5219创建新会话
        await createNewSession();
      }
      
      return data.sessions;
    } catch (error) {
      console.error('Restore sessions failed:', error);
      // 失败\u65f6创建新会话
      await createNewSession();
      return [];
    }
  }
  
  /**
   * 加载\u7279\u5b9a会话
   */
  async function loadSession(sessionKey) {
    const authStore = useAuthStore();
    const token = authStore.token;
    
    if (!token) return;
    
    try {
      loading.value = true;
      
      const res = await fetch(`${API_URL}/chat/history/${sessionKey}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (!res.ok) {
        if (res.status === 404) {
          // 会话\u4e0d\u5b58\u5728\uff0c创建新\u7684
          await createNewSession();
          return;
        }
        throw new Error('Failed to load session');
      }
      
      const data = await res.json();
      currentSession.value = {
        sessionKey: data.sessionKey,
        title: data.title
      };
      messages.value = data.messages || [];
      
      return data;
    } catch (error) {
      console.error('Load session failed:', error);
      throw error;
    } finally {
      loading.value = false;
    }
  }
  
  /**
   * 创建新会话
   */
  async function createNewSession(title = null) {
    const sessionKey = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    currentSession.value = {
      sessionKey,
      title: title || '新对话'
    };
    messages.value = [];
    
    // \u53ef\u9009\uff1a\u7acb\u5373保存\u5230\u540e\u7aef\uff08\u7a7a会话\uff09
    await saveCurrentSession();
    
    return sessionKey;
  }
  
  /**
   * \u6dfb\u52a0消息\uff08\u81ea\u52a8保存\uff09
   */
  async function addMessage(role, content, image = null) {
    const message = {
      role,
      content,
      image: image || null,
      timestamp: Date.now()
    };
    
    messages.value.push(message);
    
    // \u81ea\u52a8保存\u5230\u540e\u7aef
    await saveCurrentSession();
    
    return message;
  }
  
  /**
   * 保存当前会话\u5230\u540e\u7aef
   */
  async function saveCurrentSession() {
    if (!currentSession.value) return;
    
    const authStore = useAuthStore();
    const token = authStore.token;
    
    if (!token) return;
    
    try {
      await fetch(`${API_URL}/chat/history`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          session_key: currentSession.value.sessionKey,
          title: currentSession.value.title,
          messages: messages.value
        })
      });
    } catch (error) {
      console.error('Save failed:', error);
    }
  }
  
  /**
   * 删除会话
   */
  async function deleteSession(sessionKey) {
    const authStore = useAuthStore();
    const token = authStore.token;
    
    if (!token) return;
    
    try {
      await fetch(`${API_URL}/chat/history/${sessionKey}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      // \u4ece\u672c\u5730列表\u79fb\u9664
      sessions.value = sessions.value.filter(s => s.sessionKey !== sessionKey);
      
      // \u5982\u679c删除\u7684\u662f当前会话\uff0c\u5207\u6362\u5230\u5176\u4ed6会话\u6216创建新会话
      if (currentSession.value?.sessionKey === sessionKey) {
        if (sessions.value.length > 0) {
          await loadSession(sessions.value[0].sessionKey);
        } else {
          await createNewSession();
        }
      }
    } catch (error) {
      console.error('Delete failed:', error);
      throw error;
    }
  }
  
  /**
   * \u4fee\u6539会话标题
   */
  async function updateSessionTitle(sessionKey, title) {
    const authStore = useAuthStore();
    const token = authStore.token;
    
    if (!token) return;
    
    try {
      await fetch(`${API_URL}/chat/history/${sessionKey}/title`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ title })
      });
      
      // \u66f4新\u672c\u5730
      const session = sessions.value.find(s => s.sessionKey === sessionKey);
      if (session) session.title = title;
      if (currentSession.value?.sessionKey === sessionKey) {
        currentSession.value.title = title;
      }
    } catch (error) {
      console.error('Update title failed:', error);
    }
  }
  
  /**
   * 清空当前对话\uff08\u4f46\u4e0d删除会话\uff09
   */
  async function clearCurrentMessages() {
    messages.value = [];
    await saveCurrentSession();
  }
  
  /**
   * 发送消息\u5e76\u83b7\u53d6\u56de\u590d
   */
  async function sendMessage(message, imageBase64 = null, systemPrompt = '') {
    const authStore = useAuthStore();
    const token = authStore.token;
    
    if (!token) throw new Error('Not authenticated');
    
    // \u6dfb\u52a0\u7528\u6237消息
    await addMessage('user', message, imageBase64);
    
    // \u8c03\u7528 API
    const res = await fetch(`${API_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        message,
        image_base64: imageBase64,
        system_prompt: systemPrompt
      })
    });
    
    if (!res.ok) throw new Error('Chat request failed');
    
    const data = await res.json();
    const reply = data.choices?.[0]?.message?.content || '抱歉\uff0c出错\u4e86';
    
    // \u6dfb\u52a0\u52a9\u624b消息
    await addMessage('assistant', reply);
    
    return reply;
  }
  
  /**
   * \u6d41\u5f0f发送消息
   */
  async function sendMessageStream(message, onChunk, imageBase64 = null, systemPrompt = '') {
    const authStore = useAuthStore();
    const token = authStore.token;
    
    if (!token) throw new Error('Not authenticated');
    
    // \u6dfb\u52a0\u7528\u6237消息
    await addMessage('user', message, imageBase64);
    
    const res = await fetch(`${API_URL}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        message,
        image_base64: imageBase64,
        system_prompt: systemPrompt
      })
    });
    
    if (!res.ok) throw new Error('Chat stream request failed');
    
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let fullContent = '';
    
    // eslint-disable-next-line no-constant-condition
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      const chunk = decoder.decode(value);
      const lines = chunk.split('\n').filter(line => line.trim());
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '[DONE]') {
            // \u6d41\u7ed3\u675f\uff0c保存\u5b8c\u6574消息
            await addMessage('assistant', fullContent);
            return fullContent;
          }
          
          try {
            const json = JSON.parse(data);
            const content = json.choices?.[0]?.delta?.content;
            if (content) {
              fullContent += content;
              onChunk(content, fullContent);
            }
          } catch (e) {
            // ignore parse error
          }
        }
      }
    }
    
    // \u5982\u679c\u6ca1\u6709 [DONE]\uff0c保存\u6700\u540e\u7684\u5185\u5bb9
    if (fullContent) {
      await addMessage('assistant', fullContent);
    }
    
    return fullContent;
  }
  
  return {
    // State
    sessions,
    currentSession,
    messages,
    loading,
    // Getters
    sessionList,
    currentSessionKey,
    hasMessages,
    // Actions
    restoreSessions,
    loadSession,
    createNewSession,
    addMessage,
    deleteSession,
    updateSessionTitle,
    clearCurrentMessages,
    sendMessage,
    sendMessageStream
  };
});
