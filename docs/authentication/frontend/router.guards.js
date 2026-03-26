/**
 * Router Guards for Authentication
 */

import { useAuthStore } from '@/stores/auth'

/**
 * Require authentication
 */
export function requireAuth(to, from, next) {
  const authStore = useAuthStore()
  
  if (!authStore.isAuthenticated) {
    next({
      path: '/login',
      query: { redirect: to.fullPath }
    })
  } else {
    next()
  }
}

/**
 * Require admin role
 */
export function requireAdmin(to, from, next) {
  const authStore = useAuthStore()
  
  if (!authStore.isAuthenticated) {
    next({
      path: '/login',
      query: { redirect: to.fullPath }
    })
  } else if (!authStore.isAdmin) {
    next({
      path: '/403',
      query: { message: 'Admin access required' }
    })
  } else {
    next()
  }
}

/**
 * Require researcher or admin role
 */
export function requireResearcher(to, from, next) {
  const authStore = useAuthStore()
  
  if (!authStore.isAuthenticated) {
    next({
      path: '/login',
      query: { redirect: to.fullPath }
    })
  } else if (!authStore.isResearcher) {
    next({
      path: '/403',
      query: { message: 'Researcher access required' }
    })
  } else {
    next()
  }
}

/**
 * Redirect if already authenticated
 * (for login/register pages)
 */
export function redirectIfAuth(to, from, next) {
  const authStore = useAuthStore()
  
  if (authStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
}

/**
 * Initialize auth on app start
 */
export async function initAuth(to, from, next) {
  const authStore = useAuthStore()
  
  if (!authStore.user && authStore.accessToken) {
    try {
      await authStore.fetchUser()
    } catch (err) {
      // User fetch failed, but we'll let the route guard handle it
    }
  }
  
  next()
}
