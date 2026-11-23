import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { authApi } from '../features/auth/api/auth'
import type { User } from '../features/usuarios/types'
import { onSessionExpired } from '../shared/api/axiosInstance'
import { queryClient } from '../shared/api/queryClient'

function clearPrivateQueries() {
  queryClient.removeQueries({
    predicate: (query) => ['pedidos', 'usuarios', 'resumen'].includes(String(query.queryKey[0])),
  })
}

interface AuthStore {
  user: User | null
  loading: boolean
  checkSession: () => Promise<void>
  login: (username: string, password: string) => Promise<User>
  logout: () => Promise<void>
}

export const useAuth = create<AuthStore>()(
  persist(
    (set) => ({
      user: null,
      loading: true,
      checkSession: async () => {
        try {
          set({ user: await authApi.me() })
        } catch {
          set({ user: null })
          clearPrivateQueries()
        } finally {
          set({ loading: false })
        }
      },
      login: async (username, password) => {
        await authApi.login(username, password)
        const user = await authApi.me()
        clearPrivateQueries()
        set({ user, loading: false })
        return user
      },
      logout: async () => {
        await authApi.logout()
        clearPrivateQueries()
        set({ user: null, loading: false })
      },
    }),
    { name: 'food-store-session', partialize: (state) => ({ user: state.user }) },
  ),
)

onSessionExpired(() => {
  useAuth.setState({ user: null, loading: false })
  clearPrivateQueries()
})
