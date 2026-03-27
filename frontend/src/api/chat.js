// api/chat.js - \u4f7f\u7528 Pinia store \u8fdb\u884c\u8ba4\u8bc1
import { useAuthStore } from '@/stores/auth';
import { useChatStore } from '@/stores/chat';

const API_URL = 'https://chat.xinhai.co';
const OPENCLAW_API_URL = 'https://chat.xinhai.co';

/**
 * \u53d1\u9001\u6d88\u606f\uff08\u975e\u6d41\u5f0f\uff09
 */
export async function sendMessage(message, imageBase64 = null, systemPrompt = '') {
  const chatStore = useChatStore();
  return chatStore.sendMessage(message, imageBase64, systemPrompt);
}

/**
 * \u6d41\u5f0f\u53d1\u9001\u6d88\u606f
 */
export async function sendMessageStream(message, onChunk, imageBase64 = null, systemPrompt = '') {
  const chatStore = useChatStore();
  return chatStore.sendMessageStream(message, onChunk, imageBase64, systemPrompt);
}

/**
 * XinHai Chat API \u7c7b - \u517c\u5bb9\u65e7\u4ee3\u7801
 */
export class XinHaiChatAPI {
  constructor() {
    this.chatStore = null;
  }
  
  _getStore() {
    if (!this.chatStore) {
      this.chatStore = useChatStore();
    }
    return this.chatStore;
  }
  
  async sendMessage(message, imageBase64 = null, systemPrompt = '') {
    const store = this._getStore();
    const content = await store.sendMessage(message, imageBase64, systemPrompt);
    return { content, role: 'assistant' };
  }
  
  async sendMessageStream(message, imageBase64 = null, onChunk, systemPrompt = '') {
    const store = this._getStore();
    let content = '';
    
    await store.sendMessageStream(
      message,
      (chunk, full) => {
        content = full;
        onChunk(chunk, full);
      },
      imageBase64,
      systemPrompt
    );
    
    return { content, role: 'assistant' };
  }
}

export const chatApi = new XinHaiChatAPI();
