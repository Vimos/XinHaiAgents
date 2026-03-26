import axios from 'axios';

// OpenClaw Gateway HTTP API 配置
const OPENCLAW_API_URL = (import.meta.env.VITE_OPENCLAW_API_URL || 'http://localhost:18789').replace(/\/v1\/?$/, '');
const OPENCLAW_TOKEN = import.meta.env.VITE_OPENCLAW_TOKEN || '';

const api = axios.create({
  baseURL: OPENCLAW_API_URL,
  timeout: 300000,
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${OPENCLAW_TOKEN}`
  },
});

api.interceptors.request.use((config) => {
  console.log('[XinHaiChat] →', config.method?.toUpperCase(), config.url);
  return config;
});

api.interceptors.response.use(
  (response) => {
    console.log('[XinHaiChat] ←', response.status);
    return response;
  },
  (error) => {
    console.error('[XinHaiChat] ✗', error.response?.status || error.message);
    return Promise.reject(error);
  }
);

/**
 * XinHai Chat API - OpenClaw OpenAI 接口
 * 
 * 特点：
 * 1. 只发送当前消息，不传递历史
 * 2. 支持多模态（文本 + 图片）
 * 3. 使用标准 OpenAI 格式
 */
export class XinHaiChatAPI {
  
  constructor() {
    this.sessionKey = `xinhai_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * 发送消息（只发送当前消息，不传递历史）
   * @param {string} message - 用户消息
   * @param {string|null} imageBase64 - 图片 base64 数据（可选）
   * @param {string} systemPrompt - 系统提示词（可选）
   * @returns {Promise<{content: string, role: string}>}
   */
  async sendMessage(message, imageBase64 = null, systemPrompt = '') {
    console.log('[XinHaiChat] ========== sendMessage ==========');
    console.log('[XinHaiChat] Has image:', !!imageBase64);

    try {
      // 构建消息（只发送当前消息）
      const messages = [];
      
      // 系统提示词（可选）
      if (systemPrompt) {
        messages.push({ role: 'system', content: systemPrompt });
      }
      
      // 添加当前消息（支持多模态）
      if (imageBase64 && imageBase64.startsWith('data:image')) {
        console.log('[XinHaiChat] ✅ Sending with image');
        messages.push({
          role: 'user',
          content: [
            { type: 'text', text: message },
            { type: 'image_url', image_url: { url: imageBase64 } }
          ]
        });
      } else {
        console.log('[XinHaiChat] Sending text only');
        messages.push({
          role: 'user',
          content: message
        });
      }

      // 发送请求到 OpenClaw
      const res = await api.post('/v1/chat/completions', {
        model: 'openclaw:main',
        messages,
        temperature: 0.7,
        max_tokens: 2000,
        user: this.sessionKey
      });

      const content = res.data.choices?.[0]?.message?.content || '处理中...';
      
      return {
        content,
        role: 'assistant'
      };

    } catch (error) {
      console.error('[XinHaiChat] API error:', error);
      throw error;
    }
  }

  /**
   * 流式发送消息
   * @param {string} message - 用户消息
   * @param {string|null} imageBase64 - 图片 base64
   * @param {Function} onChunk - 收到数据块时的回调
   * @param {string} systemPrompt - 系统提示词
   */
  async sendMessageStream(message, imageBase64 = null, onChunk, systemPrompt = '') {
    console.log('[XinHaiChat] ========== sendMessageStream ==========');

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

      const res = await fetch(`${OPENCLAW_API_URL}/v1/chat/completions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${OPENCLAW_TOKEN}`
        },
        body: JSON.stringify({
          model: 'openclaw:main',
          messages,
          temperature: 0.7,
          max_tokens: 2000,
          stream: true,
          user: this.sessionKey
        })
      });

      const reader = res.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let content = '';
      // eslint-disable-next-line no-constant-condition
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n').filter(line => line.trim());

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

      return { content, role: 'assistant' };

    } catch (error) {
      console.error('[XinHaiChat] Stream error:', error);
      throw error;
    }
  }
}

export const chatApi = new XinHaiChatAPI();
