import { api } from '../../../shared/api/axiosInstance'
import type { User } from '../types'
export const userApi = {
  list: async () => (await api.get<User[]>('/admin/usuarios')).data,
  setDisabled: async (user: User) =>
    (await api.post<User>(`/admin/usuarios/${user.id}/${user.disabled ? 'activar' : 'desactivar'}`))
      .data,
}
