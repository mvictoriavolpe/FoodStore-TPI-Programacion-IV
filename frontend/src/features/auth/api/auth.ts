import { api } from '../../../shared/api/axiosInstance'
import type { User } from '../../usuarios/types'
export interface RegisterInput {
  username: string
  full_name: string
  email: string
  password: string
}
export const authApi = {
  register: async (data: RegisterInput) => (await api.post<User>('/auth/register', data)).data,
  login: async (username: string, password: string) => {
    await api.post('/auth/token', new URLSearchParams({ username, password }))
  },
  me: async () => (await api.get<User>('/auth/me')).data,
  logout: async () => {
    await api.post('/auth/logout')
  },
}
