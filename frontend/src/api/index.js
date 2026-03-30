/**
 * 统一 API 层 - 所有后端通信集中管理
 */

const API_BASE = process.env.VUE_APP_API_URL || 'https://chat.xinhai.co';

function getToken() {
  return localStorage.getItem('token');
}

function getHeaders() {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getToken()}`
  };
}

// ============ 认证 API ============
export const authApi = {
  async login(credentials) {
    const res = await fetch(`${API_BASE}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials)
    });
    if (!res.ok) throw new Error('登录失败');
    return res.json();
  },

  async register(data) {
    const res = await fetch(`${API_BASE}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('注册失败');
    return res.json();
  },

  async getProfile() {
    const res = await fetch(`${API_BASE}/api/auth/me`, {
      headers: getHeaders()
    });
    if (!res.ok) throw new Error('获取用户信息失败');
    return res.json();
  }
};

// ============ 对话 API ============
export const chatApi = {
  // 获取历史列表
  async getHistory(sidebar = null) {
    const url = sidebar 
      ? `${API_BASE}/api/chat/history?sidebar=${sidebar}`
      : `${API_BASE}/api/chat/history`;
    const res = await fetch(url, { headers: getHeaders() });
    if (!res.ok) throw new Error('获取历史失败');
    return res.json();
  },

  // 获取单个会话
  async getSession(sessionKey) {
    const res = await fetch(`${API_BASE}/api/chat/history/${sessionKey}`, {
      headers: getHeaders()
    });
    if (!res.ok) throw new Error('获取会话失败');
    return res.json();
  },

  // 保存会话
  async saveSession({ sessionKey, sidebar, title, messages }) {
    const res = await fetch(`${API_BASE}/api/chat/history`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ sessionKey, sidebar, title, messages })
    });
    if (!res.ok) throw new Error('保存失败');
    return res.json();
  },

  // 删除会话
  async deleteSession(sessionKey) {
    const res = await fetch(`${API_BASE}/api/chat/history/${sessionKey}`, {
      method: 'DELETE',
      headers: getHeaders()
    });
    if (!res.ok) throw new Error('删除失败');
    return res.json();
  },

  // 发送消息（流式）
  async sendMessage({ messages, sidebar, sessionKey, onChunk, onError, onComplete }) {
    const response = await fetch(`${API_BASE}/api/chat/stream`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        messages,
        sidebar,
        session_key: sessionKey,
        stream: true
      })
    });

    if (!response.ok) {
      throw new Error('请求失败');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let content = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') {
              onComplete?.(content);
              return content;
            }
            try {
              const parsed = JSON.parse(data);
              const delta = parsed.choices?.[0]?.delta?.content || '';
              content += delta;
              onChunk?.(content, delta);
            } catch (e) {
              // 忽略解析错误
            }
          }
        }
      }
    } catch (error) {
      onError?.(error);
      throw error;
    }

    return content;
  }
};

// ============ 模拟 API ============
export const simulationApi = {
  async create(configYaml) {
    const res = await fetch(`${API_BASE}/api/simulation/create`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ config_yaml: configYaml })
    });
    if (!res.ok) throw new Error('创建模拟失败');
    return res.json();
  },

  async next(inputMessages = []) {
    const res = await fetch(`${API_BASE}/api/simulation/next`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ input_messages: inputMessages })
    });
    if (!res.ok) throw new Error('模拟步骤失败');
    return res.json();
  },

  async reset() {
    const res = await fetch(`${API_BASE}/api/simulation/reset`, {
      method: 'POST',
      headers: getHeaders()
    });
    if (!res.ok) throw new Error('重置失败');
    return res.json();
  },

  async getStatus() {
    const res = await fetch(`${API_BASE}/api/simulation/status`, {
      headers: getHeaders()
    });
    if (!res.ok) throw new Error('获取状态失败');
    return res.json();
  }
};

export default { auth: authApi, chat: chatApi, simulation: simulationApi };
