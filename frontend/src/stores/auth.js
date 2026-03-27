import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useChatStore } from './chat';

const API_URL = 'https://chat.xinhai.co';  // 认证服务地址

export const useAuthStore = defineStore('auth', () => {
  // ============ State ============
  const token = ref(localStorage.getItem('token') || '');
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'));
  const loading = ref(false);
  const error = ref('');
  
  // ============ Getters ============
  const isLoggedIn = computed(() => !!token.value);
  const currentUser = computed(() => user.value);
  
  // ============ Actions ============
  
  async function register(username, email, password) {
    loading.value = true;
    error.value = '';
    
    try {
      const res = await fetch(`${API_URL}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password })
      });
      
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || '注册失败');
      }
      
      const data = await res.json();
      token.value = data.token;
      user.value = { id: data.user_id, username: data.username };
      
      localStorage.setItem('token', data.token);
      localStorage.setItem('user', JSON.stringify(user.value));
      
      // 登录成功后恢复对话历史
      const chatStore = useChatStore();
      await chatStore.restoreSessions();
      
      return data;
    } catch (err) {
      error.value = err.message;
      throw err;
    } finally {
      loading.value = false;
    }
  }
  
  async function login(username, password) {
    loading.value = true;
    error.value = '';
    
    try {
      const res = await fetch(`${API_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || '登录失败');
      }
      
      const data = await res.json();
      token.value = data.token;
      user.value = { id: data.user_id, username: data.username };
      
      localStorage.setItem('token', data.token);
      localStorage.setItem('user', JSON.stringify(user.value));
      
      // 登录成功后\u81ea\u52a8恢复对话历史
      const chatStore = useChatStore();
      await chatStore.restoreSessions();
      
      return data;
    } catch (err) {
      error.value = err.message;
      throw err;
    } finally {
      loading.value = false;
    }
  }
  
  function logout() {
    token.value = '';
    user.value = null;
    error.value = '';
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }
  
  function getAuthHeaders() {
    return {
      'Authorization': `Bearer ${token.value}`,
      'Content-Type': 'application/json'
    };
  }
  
  // \u521d\u59cb\u5316\uff1a\u68c0\u67e5\u662f\u5426\u5df2登录
  async function init() {
    if (token.value && user.value) {
      try {
        // \u9a8c\u8bc1 token \u662f\u5426\u6709\u6548
        const res = await fetch(`${API_URL}/api/auth/me`, {
          headers: { 'Authorization': `Bearer ${token.value}` }
        });
        
        if (!res.ok) {
          // token \u65e0\u6548\uff0c\u6e05\u9664
          logout();
          return false;
        }
        
        // 恢复对话历史
        const chatStore = useChatStore();
        await chatStore.restoreSessions();
        return true;
      } catch (err) {
        logout();
        return false;
      }
    }
    return false;
  }
  
  return {
    // State
    token,
    user,
    loading,
    error,
    // Getters
    isLoggedIn,
    currentUser,
    // Actions
    register,
    login,
    logout,
    getAuthHeaders,
    init
  };
});
