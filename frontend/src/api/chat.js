import axios from 'axios';

// OpenClaw Gateway HTTP API 配置
const OPENCLAW_API_URL = '/openclaw';

// 支持多种环境变量命名（Vue CLI, Vite）
function getToken() {
  // Vue CLI 使用 process.env
  if (typeof process !== 'undefined' && process.env) {
    const token = process.env.VUE_APP_OPENCLAW_TOKEN?.trim()
      || process.env.VITE_OPENCLAW_TOKEN?.trim()
      || process.env.OPENCLAW_TOKEN?.trim();
    if (token) return token;
  }
  
  // Vite 使用 import.meta.env
  if (typeof import.meta !== 'undefined' && import.meta.env) {
    const token = import.meta.env.VITE_OPENCLAW_TOKEN?.trim()
      || import.meta.env.VUE_APP_OPENCLAW_TOKEN?.trim()
      || import.meta.env.OPENCLAW_TOKEN?.trim();
    if (token) return token;
  }
  
  return '';
}

const OPENCLAW_TOKEN = getToken();

// 调试日志
console.log('[XinHaiChat] Token status:', OPENCLAW_TOKEN ? '✓ configured' : '✗ missing');

if (!OPENCLAW_TOKEN) {
  console.warn('[XinHaiChat] ⚠️ No token found!');
  console.warn('[XinHaiChat] Please create frontend/.env file with:');
  console.warn('[XinHaiChat] VUE_APP_OPENCLAW_TOKEN=your_token_here');
}

const api = axios.create({
  baseURL: OPENCLAW_API_URL,
  timeout: 300000,
  headers: {
    'Content-Type': 'application/json',
    ...(OPENCLAW_TOKEN ? { 'Authorization': `Bearer ${OPENCLAW_TOKEN}` } : {})
  },
});

api.interceptors.request.use((config) => {
  console.log('[XinHaiChat] →', config.method?.toUpperCase(), config.url,
    config.headers.Authorization ? '(with token)' : '(no token)');
  return config;
});

api.interceptors.response.use(
  (response) => {
    console.log('[XinHaiChat] ←', response.status);
    return response;
  },
  (error) => {
    console.error('[XinHaiChat] ✗', error.response?.status || error.message);
    if (error.response?.status === 401) {
      console.error('[XinHaiChat] Token invalid. Check VUE_APP_OPENCLAW_TOKEN in .env file');
    }
    return Promise.reject(error);
  }
);

/**
 * XinHai Chat API - OpenClaw OpenAI 接口
 */
export class XinHaiChatAPI {
  
  constructor() {
    this.sessionKey = `xinhai_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  async sendMessage(message, imageBase64 = null, systemPrompt = '') {
    console.log('[XinHaiChat] ========== sendMessage ==========');
    if (!OPENCLAW_TOKEN) {
      throw new Error('OpenClaw token not configured. Please set VUE_APP_OPENCLAW_TOKEN in .env file');
    }

    try {
      const messages = [];
      
      if (systemPrompt) {
        messages.push({ role: 'system', content: systemPrompt });
      }
      
      if (imageBase64 && imageBase64.startsWith('data:image')) {
        messages.push({
          role: 'user',
          content: [
            { type: 'text', text: message },
            { type: 'image_url', image_url: { url: imageBase64 } }
          ]
        });
      } else {
        messages.push({ role: 'user', content: message });
      }

      const res = await api.post('/v1/chat/completions', {
        model: 'openclaw:main',
        messages,
        temperature: 0.7,
        max_tokens: 2000,
        user: this.sessionKey
      });

      const content = res.data.choices?.[0]?.message?.content || '处理中...';
      
      return { content, role: 'assistant' };

    } catch (error) {
      console.error('[XinHaiChat] API error:', error);
      throw error;
    }
  }

  async sendMessageStream(message, imageBase64 = null, onChunk, systemPrompt = '') {
    console.log('[XinHaiChat] ========== sendMessageStream ==========');
    if (!OPENCLAW_TOKEN) {
      throw new Error('OpenClaw token not configured. Please set VUE_APP_OPENCLAW_TOKEN in .env file');
    }

    try {
      const messages = [];
      
      if (systemPrompt) {
        messages.push({ role: 'system', content: systemPrompt });
      }
      
      if (imageBase64 && imageBase64.startsWith('data:image')) {
        messages.push({
          role: 'user',
          content: [
            { type: 'text', text: message },
            { type: 'image_url', image_url: { url: imageBase64 } }
          ]
        });
      } else {
        messages.push({ role: 'user', content: message });
      }

      let content = '';
      
      await api.post('/v1/chat/completions', {
        model: 'openclaw:main',
        messages,
        temperature: 0.7,
        max_tokens: 2000,
        stream: true,
        user: this.sessionKey
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
                  onChunk(delta, content);
                }
              } catch (e) {
                // 忽略解析错误
              }
            }
          }
        }
      });

      return { content, role: 'assistant' };

    } catch (error) {
      console.error('[XinHaiChat] Stream error:', error);
      throw error;
    }
  }
}

export const chatApi = new XinHaiChatAPI();
