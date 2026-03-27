<template>
  <div class="login-container">
    <div class="login-box">
      <div class="logo">
        <span class="icon">🌊</span>
        <h1>XinHai \u667a\u80fd\u4f53</h1>
        <p class="subtitle">\u767b\u5f55\u540e\u5f00\u59cb\u5bf9\u8bdd</p>
      </div>
      
      <div class="tabs">
        <button 
          :class="['tab', { active: isLogin }]" 
          @click="isLogin = true"
        >
          \u767b\u5f55
        </button>
        <button 
          :class="['tab', { active: !isLogin }]" 
          @click="isLogin = false"
        >
          \u6ce8\u518c
        </button>
      </div>
      
      <form @submit.prevent="handleSubmit" class="form">
        <div class="input-group">
          <input 
            v-model="form.username" 
            type="text"
            placeholder="\u7528\u6237\u540d" 
            required 
            :disabled="loading"
          />
        </div>
        
        <div class="input-group" v-if="!isLogin">
          <input 
            v-model="form.email" 
            type="email"
            placeholder="\u90ae\u7bb1" 
            required 
            :disabled="loading"
          />
        </div>
        
        <div class="input-group">
          <input 
            v-model="form.password" 
            type="password" 
            placeholder="\u5bc6\u7801" 
            required 
            :disabled="loading"
          />
        </div>
        
        <button type="submit" class="submit-btn" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>{{ isLogin ? '\u767b\u5f55' : '\u6ce8\u518c' }}</span>
        </button>
      </form>
      
      <p v-if="error" class="error">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const authStore = useAuthStore();

const isLogin = ref(true);
const loading = ref(false);
const error = ref('');

const form = reactive({
  username: '',
  email: '',
  password: ''
});

async function handleSubmit() {
  loading.value = true;
  error.value = '';
  
  try {
    if (isLogin.value) {
      await authStore.login(form.username, form.password);
    } else {
      await authStore.register(form.username, form.email, form.password);
    }
    
    // \u767b\u5f55/\u6ce8\u518c\u6210\u529f\uff0c\u8df3\u8f6c\u5230\u4e3b\u9875
    router.push('/');
  } catch (err) {
    error.value = err.message || '\u64cd\u4f5c\u5931\u8d25\uff0c\u8bf7\u91cd\u8bd5';
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-box {
  background: white;
  border-radius: 16px;
  padding: 40px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}

.logo {
  text-align: center;
  margin-bottom: 30px;
}

.icon {
  font-size: 48px;
  display: block;
  margin-bottom: 10px;
}

h1 {
  margin: 0;
  font-size: 24px;
  color: #333;
}

.subtitle {
  color: #666;
  margin-top: 8px;
}

.tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 24px;
}

.tab {
  flex: 1;
  padding: 12px;
  border: none;
  background: #f0f0f0;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.tab.active {
  background: #667eea;
  color: white;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.input-group input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.input-group input:focus {
  outline: none;
  border-color: #667eea;
}

.submit-btn {
  padding: 14px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.submit-btn:hover:not(:disabled) {
  background: #5568d3;
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #fff;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error {
  color: #e74c3c;
  text-align: center;
  margin-top: 16px;
  font-size: 14px;
}
</style>
