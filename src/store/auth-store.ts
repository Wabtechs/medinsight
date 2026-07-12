import { create } from 'zustand'
import type { User } from '@/types'
import { mockUsers } from '@/lib/mock-data'

interface AuthState {
  user: User | null
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  updateProfile: (updates: Partial<User>) => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  login: async (email: string, _password: string) => {
    const found = mockUsers.find((u) => u.email === email)
    if (!found) {
      throw new Error('Identifiant ou mot de passe incorrect')
    }
    set({
      user: {
        ...found,
        lastLogin: new Date().toISOString(),
      },
    })
  },

  logout: () => set({ user: null }),

  updateProfile: (updates) =>
    set((state) => ({
      user: state.user ? { ...state.user, ...updates } : null,
    })),
}))
