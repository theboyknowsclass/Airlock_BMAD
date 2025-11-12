import { create } from 'zustand'

interface AuthState {
  token: string | null
  isAuthenticated: boolean
  setToken: (token: string | null) => void
  logout: () => void
}

// Zustand store for authentication
export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem('access_token'),
  isAuthenticated: !!localStorage.getItem('access_token'),
  setToken: (token) => {
    if (token) {
      localStorage.setItem('access_token', token)
      set({ token, isAuthenticated: true })
    } else {
      localStorage.removeItem('access_token')
      set({ token: null, isAuthenticated: false })
    }
  },
  logout: () => {
    localStorage.removeItem('access_token')
    set({ token: null, isAuthenticated: false })
  },
}))

