import { create } from 'zustand'

interface User {
  sid: string
  username: string
  displayName: string
  email: string
  site: string
  groups: string[]
}

interface AuthState {
  accessToken: string | null
  refreshToken: string | null
  user: User | null
  isAuthenticated: boolean
  mfaRequired: boolean
  setTokens: (access: string, refresh: string) => void
  setUser: (user: User) => void
  setMfaRequired: (required: boolean) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: localStorage.getItem('accessToken'),
  refreshToken: localStorage.getItem('refreshToken'),
  user: null,
  isAuthenticated: !!localStorage.getItem('accessToken'),
  mfaRequired: false,

  setTokens: (access, refresh) => {
    localStorage.setItem('accessToken', access)
    localStorage.setItem('refreshToken', refresh)
    set({ accessToken: access, refreshToken: refresh, isAuthenticated: true })
  },

  setUser: (user) => set({ user }),

  setMfaRequired: (required) => set({ mfaRequired: required }),

  logout: () => {
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
    set({
      accessToken: null,
      refreshToken: null,
      user: null,
      isAuthenticated: false,
      mfaRequired: false,
    })
  },
}))