// api/chat.js - 使用 Pinia store 进行认证
import axios from 'axios';
import { useChatStore } from '@/stores/chat';

// 认证服务地址（不是直接调用 XinHai 智能体）
const AUTH_API_URL = 'https://chat.xinhai.co';

// 创建 axios 实例供 ChatContainer.vue 使用
const api = axios.create({
  baseURL: AUTH_API_URL,
  timeout: 300000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器：自动添加认证头
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

/**
 * 发送消息（非流式）
 */
export async function sendMessage(message, imageBase64 = null, systemPrompt = '') {
  const chatStore = useChatStore();
  return chatStore.sendMessage(message, imageBase64, systemPrompt);
}

/**
 * 流式发送消息
 */
export async function sendMessageStream(message, onChunk, imageBase64 = null, systemPrompt = '') {
  const chatStore = useChatStore();
  return chatStore.sendMessageStream(message, onChunk, imageBase64, systemPrompt);
}

/**
 * XinHai Chat API 类 - 兼容旧代码
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
export { api, AUTH_API_URL };
