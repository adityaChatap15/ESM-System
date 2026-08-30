import { useAuth } from '@/context/AuthContext'
import { apiRequest, ApiError } from '@/lib/api'

/**
 * Wraps apiRequest with the logged-in user's token, and logs the user
 * out automatically if the backend says the token is no longer valid.
 */
export function useApi() {
  const { token, logout } = useAuth()

  return async function request(path, options = {}) {
    try {
      return await apiRequest(path, { ...options, token })
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        logout()
      }
      throw error
    }
  }
}
