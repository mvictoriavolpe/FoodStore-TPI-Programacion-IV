import { api } from '../../../shared/api/axiosInstance'
import type { Category, CategoryInput } from '../types'
export const categoryApi = {
  list: async () => (await api.get<Category[]>('/categorias')).data,
  save: async (data: CategoryInput, id: number | null) =>
    (id
      ? await api.put<Category>(`/categorias/${id}`, data)
      : await api.post<Category>('/categorias', data)
    ).data,
  remove: async (id: number) => {
    await api.delete(`/categorias/${id}`)
  },
}
