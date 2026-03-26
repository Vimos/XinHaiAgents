/**
 * Authentication Store (Pinia)
 * 
 * Manages user authentication state, tokens, and API calls
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const accessToken = ref(localStorage.getItem('access_token'))
  const refreshToken = ref(localStorage.getItem('refresh_token'))
  const loading = ref(false)
  const error = ref(null)
  
  const router = useRouter()
  
  // Getters
  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isResearcher = computed(() => ['admin', 'researcher'].includes(user.value?.role))
  
  // Actions
  
  /**
   * Initialize auth state on app load
   */
  async function init() {
    if (accessToken.value) {
      try {
        await fetchUser()
      } catch (err) {
        // Token expired or invalid, try refresh
        try {
          await refreshAccessToken()
        } catch (refreshErr) {
          logout()
        }
      }
    }
  }
  
  /**
   * User login
   */
  async function login(credentials) {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.post('/auth/login', credentials)
      
      // Store tokens
      accessToken.value = response.data.access_token
      refreshToken.value = response.data.refresh_token
      
      localStorage.setItem('access_token', response.data.access_token)
      localStorage.setItem('refresh_token', response.data.refresh_token)
      
      // Fetch user info
      await fetchUser()
      
      return true
    } catch (err) {
      error.value = err.response?.data?.detail || 'Login failed'
      return false
    } finally {
      loading.value = false
    }
  }
  
  /**
   * User registration
   */
  async function register(userData) {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.post('/auth/register', userData)
      return { success: true, data: response.data }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Registration failed'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Fetch current user info
   */
  async function fetchUser() {
    try {
      const response = await api.get('/auth/me')
      user.value = response.data
      return response.data
    } catch (err) {
      throw err
    }
  }
  
  /**
   * Refresh access token
   */
  async function refreshAccessToken() {
    try {
      const response = await api.post('/auth/refresh', {
        refresh_token: refreshToken.value
      })
      
      accessToken.value = response.data.access_token
      refreshToken.value = response.data.refresh_token
      
      localStorage.setItem('access_token', response.data.access_token)
      localStorage.setItem('refresh_token', response.data.refresh_token)
      
      return true
    } catch (err) {
      logout()
      throw err
    }
  }
  
  /**
   * Logout user
   */
  async function logout() {
    try {
      if (accessToken.value) {
        await api.post('/auth/logout')
      }
    } catch (err) {
      // Ignore errors during logout
    } finally {
      // Clear state
      user.value = null
      accessToken.value = null
      refreshToken.value = null
      
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      
      router.push('/login')
    }
  }
  
  /**
   * Update user profile
   */
  async function updateProfile(profileData) {
    loading.value = true
    
    try {
      const response = await api.put('/auth/me', profileData)
      user.value = response.data
      return { success: true }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Update failed'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Change password
   */
  async function changePassword(passwordData) {
    loading.value = true
    
    try {
      await api.post('/auth/change-password', passwordData)
      return { success: true }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Password change failed'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }
  
  return {
    // State
    user,
    accessToken,
    refreshToken,
    loading,
    error,
    
    // Getters
    isAuthenticated,
    isAdmin,
    isResearcher,
    
    // Actions
    init,
    login,
    register,
    fetchUser,
    refreshAccessToken,
    logout,
    updateProfile,
    changePassword
  }
})
