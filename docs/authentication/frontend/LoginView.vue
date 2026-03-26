<template>
  <div class="login-container">
    <div class="login-card">
      <h1 class="title">XinHaiAgents</h1>
      <p class="subtitle">Multi-Agent Simulation Platform</p>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <!-- Username/Email -->
        <div class="form-group">
          <label for="username">Username or Email</label>
          <input
            id="username"
            v-model="form.username"
            type="text"
            required
            placeholder="Enter your username or email"
            :disabled="authStore.loading"
          />
        </div>
        
        <!-- Password -->
        <div class="form-group">
          <label for="password">Password</label>
          <div class="password-input">
            <input
              id="password"
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              required
              placeholder="Enter your password"
              :disabled="authStore.loading"
            />
            <button
              type="button"
              class="toggle-password"
              @click="showPassword = !showPassword"
            >
              {{ showPassword ? '🙈' : '👁️' }}
            </button>
          </div>
        </div>
        
        <!-- Remember Me -->
        <div class="form-group remember">
          <label class="checkbox-label">
            <input
              v-model="form.remember"
              type="checkbox"
              :disabled="authStore.loading"
            />
            Remember me
          </label>
          <router-link to="/forgot-password" class="forgot-link">
            Forgot password?
          </router-link>
        </div>
        
        <!-- Error Message -->
        <div v-if="authStore.error" class="error-message">
          {{ authStore.error }}
        </div>
        
        <!-- Submit Button -->
        <button
          type="submit"
          class="submit-btn"
          :disabled="authStore.loading || !isValid"
        >
          <span v-if="authStore.loading">Logging in...</span>
          <span v-else>Sign In</span>
        </button>
      </form>
      
      <!-- Register Link -->
      <div class="register-link">
        Don't have an account?
        <router-link to="/register">Sign up</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// Form state
const form = ref({
  username: '',
  password: '',
  remember: false
})

const showPassword = ref(false)

// Validation
const isValid = computed(() => {
  return form.value.username.length >= 3 && form.value.password.length >= 8
})

// Handle login
async function handleLogin() {
  if (!isValid.value) return
  
  const success = await authStore.login({
    username: form.value.username,
    password: form.value.password
  })
  
  if (success) {
    // Redirect to intended page or dashboard
    const redirect = router.currentRoute.value.query.redirect || '/'
    router.push(redirect)
  }
}

// Check if already logged in
onMounted(() => {
  if (authStore.isAuthenticated) {
    router.push('/')
  }
})
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

.login-card {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

.title {
  font-size: 28px;
  font-weight: 700;
  text-align: center;
  color: #333;
  margin-bottom: 8px;
}

.subtitle {
  text-align: center;
  color: #666;
  margin-bottom: 30px;
  font-size: 14px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.form-group input[type="text"],
.form-group input[type="password"] {
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

.password-input {
  position: relative;
}

.toggle-password {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
}

.remember {
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #666;
}

.forgot-link {
  font-size: 14px;
  color: #667eea;
  text-decoration: none;
}

.forgot-link:hover {
  text-decoration: underline;
}

.error-message {
  background: #fee;
  color: #c33;
  padding: 12px;
  border-radius: 6px;
  font-size: 14px;
}

.submit-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 14px;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.register-link {
  text-align: center;
  margin-top: 24px;
  font-size: 14px;
  color: #666;
}

.register-link a {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.register-link a:hover {
  text-decoration: underline;
}
</style>
