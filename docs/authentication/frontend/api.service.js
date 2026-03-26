/**
 * API Service with JWT Interceptor
 */

import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

// Create axios instance
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor - add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - handle token refresh
let isRefreshing = false
let failedQueue = []

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    
    // If error is not 401 or request already retried, reject
    if (error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(error)
    }
    
    // If already refreshing, queue the request
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject })
      })
        .then(token => {
          originalRequest.headers.Authorization = `Bearer ${token}`
          return api(originalRequest)
        })
        .catch(err => Promise.reject(err))
    }
    
    originalRequest._retry = true
    isRefreshing = true
    
    const refreshToken = localStorage.getItem('refresh_token')
    
    if (!refreshToken) {
      // No refresh token, logout
      const authStore = useAuthStore()
      authStore.logout()
      router.push('/login')
      return Promise.reject(error)
    }
    
    try {
      // Try to refresh token
      const response = await axios.post(
        `${api.defaults.baseURL}/auth/refresh`,
        { refresh_token: refreshToken }
      )
      
      const { access_token, refresh_token } = response.data
      
      // Store new tokens
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)
      
      // Update auth store
      const authStore = useAuthStore()
      authStore.accessToken = access_token
      authStore.refreshToken = refresh_token
      
      // Process queued requests
      processQueue(null, access_token)
      
      // Retry original request
      originalRequest.headers.Authorization = `Bearer ${access_token}`
      return api(originalRequest)
      
    } catch (refreshError) {
      // Refresh failed, logout
      processQueue(refreshError, null)
      const authStore = useAuthStore()
      authStore.logout()
      router.push('/login')
      return Promise.reject(refreshError)
      
    } finally {
      isRefreshing = false
    }
  }
)

export default api
