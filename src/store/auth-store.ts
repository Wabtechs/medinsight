import { create } from 'zustand'
import type { User } from '@/types'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

interface AuthState {
  user: User | null
  token: string | null
  refreshToken: string | null
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  updateProfile: (updates: Partial<User>) => void
}

function mapBackendUser(bu: Record<string, unknown>): User {
  const role = (bu.role as string).toLowerCase()
  return {
    id: bu.id as string,
    email: bu.email as string,
    name: `${bu.firstname || ''} ${bu.lastname || ''}`.trim() || bu.email as string,
    role: role as User['role'],
    facility: bu.facility_id as string,
    avatar: `https://api.dicebear.com/7.x/avataaars/svg?seed=${bu.email}`,
    createdAt: bu.created_at as string,
    lastLogin: new Date().toISOString(),
    isActive: bu.is_active as boolean,
  }
}

function loadSession(): { user: User | null; token: string | null; refreshToken: string | null } {
  try {
    const raw = localStorage.getItem('medinsight_user')
    const token = localStorage.getItem('medinsight_token')
    const refreshToken = localStorage.getItem('medinsight_refresh_token')
    if (raw && token) {
      return { user: JSON.parse(raw), token, refreshToken }
    }
  } catch { /* ignore */ }
  return { user: null, token: null, refreshToken: null }
}

function saveSession(user: User, token: string, refreshToken: string) {
  localStorage.setItem('medinsight_user', JSON.stringify(user))
  localStorage.setItem('medinsight_token', token)
  localStorage.setItem('medinsight_refresh_token', refreshToken)
}

function clearSession() {
  localStorage.removeItem('medinsight_user')
  localStorage.removeItem('medinsight_token')
  localStorage.removeItem('medinsight_refresh_token')
}

const saved = loadSession()

export const useAuthStore = create<AuthState>((set) => ({
  user: saved.user,
  token: saved.token,
  refreshToken: saved.refreshToken,

  login: async (email: string, password: string) => {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })

    if (!res.ok) {
      throw new Error('Identifiant ou mot de passe incorrect')
    }

    const data = await res.json()
    const token = data.access_token

    const userRes = await fetch(`${API_BASE}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    })

    let user: User
    if (userRes.ok) {
      const backendUser = await userRes.json()
      user = mapBackendUser(backendUser)
    } else {
      const payload = JSON.parse(atob(token.split('.')[1]))
      user = {
        id: payload.sub,
        email,
        name: email,
        role: 'admin',
        createdAt: new Date().toISOString(),
        isActive: true,
      }
    }

    saveSession(user, token, data.refresh_token || '')
    set({ user, token, refreshToken: data.refresh_token || null })
  },

  logout: () => {
    clearSession()
    set({ user: null, token: null, refreshToken: null })
  },

  updateProfile: (updates) =>
    set((state) => ({
      user: state.user ? { ...state.user, ...updates } : null,
    })),
}))
