import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useAuthStore } from './auth';

const API_URL = 'https://chat.xinhai.co';  // \u8ba4\u8bc1\u670d\u52a1\u5730\u5740

export const useChatStore = defineStore('chat', () => {
  // ============ State ============
  const sessions = ref([]);  // \u4f1a\u8bdd\u5217\u8868
  const currentSession = ref(null);  // \u5f53\u524d\u4f1a\u8bdd
  const messages = ref([]);  // \u5f53\u524d\u5bf9\u8bdd\u6d88\u606f
  const loading = ref(false);
  
  // ============ Getters ============
  const sessionList = computed(() => sessions.value);
  const currentSessionKey = computed(() => currentSession.value?.sessionKey);
  const hasMessages = computed(() => messages.value.length > 0);
  
  // ============ Actions ============
  
  /**
   * \u767b\u5f55\u540e\u6062\u590d\uff1a\u62c9\u53d6\u7528\u6237\u7684\u6240\u6709\u4f1a\u8bdd\u5217\u8868
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
      
      // \u5982\u679c\u6709\u5386\u53f2\u4f1a\u8bdd\uff0c\u52a0\u8f7d\u6700\u8fd1\u7684\u4e00\u4e2a
      if (sessions.value.length > 0) {
        await loadSession(sessions.value[0].sessionKey);
      } else {
        // \u6ca1\u6709\u5386\u53f2\u5219\u521b\u5efa\u65b0\u4f1a\u8bdd
        await createNewSession();
      }
      
      return data.sessions;
    } catch (error) {
      console.error('Restore sessions failed:', error);
      // \u5931\u8d25\u65f6\u521b\u5efa\u65b0\u4f1a\u8bdd
      await createNewSession();
      return [];
    }
  }
  
  /**
   * \u52a0\u8f7d\u7279\u5b9a\u4f1a\u8bdd
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
          // \u4f1a\u8bdd\u4e0d\u5b58\u5728\uff0c\u521b\u5efa\u65b0\u7684
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
   * \u521b\u5efa\u65b0\u4f1a\u8bdd
   */
  async function createNewSession(title = null) {
    const sessionKey = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    currentSession.value = {
      sessionKey,
      title: title || '\u65b0\u5bf9\u8bdd'
    };
    messages.value = [];
    
    // \u53ef\u9009\uff1a\u7acb\u5373\u4fdd\u5b58\u5230\u540e\u7aef\uff08\u7a7a\u4f1a\u8bdd\uff09
    await saveCurrentSession();
    
    return sessionKey;
  }
  
  /**
   * \u6dfb\u52a0\u6d88\u606f\uff08\u81ea\u52a8\u4fdd\u5b58\uff09
   */
  async function addMessage(role, content, image = null) {
    const message = {
      role,
      content,
      image: image || null,
      timestamp: Date.now()
    };
    
    messages.value.push(message);
    
    // \u81ea\u52a8\u4fdd\u5b58\u5230\u540e\u7aef
    await saveCurrentSession();
    
    return message;
  }
  
  /**
   * \u4fdd\u5b58\u5f53\u524d\u4f1a\u8bdd\u5230\u540e\u7aef
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
   * \u5220\u9664\u4f1a\u8bdd
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
      
      // \u4ece\u672c\u5730\u5217\u8868\u79fb\u9664
      sessions.value = sessions.value.filter(s => s.sessionKey !== sessionKey);
      
      // \u5982\u679c\u5220\u9664\u7684\u662f\u5f53\u524d\u4f1a\u8bdd\uff0c\u5207\u6362\u5230\u5176\u4ed6\u4f1a\u8bdd\u6216\u521b\u5efa\u65b0\u4f1a\u8bdd
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
   * \u4fee\u6539\u4f1a\u8bdd\u6807\u9898
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
      
      // \u66f4\u65b0\u672c\u5730
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
   * \u6e05\u7a7a\u5f53\u524d\u5bf9\u8bdd\uff08\u4f46\u4e0d\u5220\u9664\u4f1a\u8bdd\uff09
   */
  async function clearCurrentMessages() {
    messages.value = [];
    await saveCurrentSession();
  }
  
  /**
   * \u53d1\u9001\u6d88\u606f\u5e76\u83b7\u53d6\u56de\u590d
   */
  async function sendMessage(message, imageBase64 = null, systemPrompt = '') {
    const authStore = useAuthStore();
    const token = authStore.token;
    
    if (!token) throw new Error('Not authenticated');
    
    // \u6dfb\u52a0\u7528\u6237\u6d88\u606f
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
    const reply = data.choices?.[0]?.message?.content || '\u62b1\u6b49\uff0c\u51fa\u9519\u4e86';
    
    // \u6dfb\u52a0\u52a9\u624b\u6d88\u606f
    await addMessage('assistant', reply);
    
    return reply;
  }
  
  /**
   * \u6d41\u5f0f\u53d1\u9001\u6d88\u606f
   */
  async function sendMessageStream(message, onChunk, imageBase64 = null, systemPrompt = '') {
    const authStore = useAuthStore();
    const token = authStore.token;
    
    if (!token) throw new Error('Not authenticated');
    
    // \u6dfb\u52a0\u7528\u6237\u6d88\u606f
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
            // \u6d41\u7ed3\u675f\uff0c\u4fdd\u5b58\u5b8c\u6574\u6d88\u606f
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
    
    // \u5982\u679c\u6ca1\u6709 [DONE]\uff0c\u4fdd\u5b58\u6700\u540e\u7684\u5185\u5bb9
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
