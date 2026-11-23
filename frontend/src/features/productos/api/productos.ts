import { api } from '../../../shared/api/axiosInstance'
import type { Page } from '../../../shared/api/types'
import type { Product, ProductInput, ProductFilters } from '../types'
export const productApi = {
  list: async (filters: ProductFilters = {}) =>
    (await api.get<Page<Product>>('/productos', { params: filters })).data,
  save: async (data: ProductInput, id: number | null) =>
    (id
      ? await api.put<Product>(`/productos/${id}`, data)
      : await api.post<Product>('/productos', data)
    ).data,
  stock: async (id: number, stock: number, disponible: boolean) =>
    (await api.patch<Product>(`/productos/${id}/stock`, { stock, disponible })).data,
  availability: async (id: number, disponible: boolean) =>
    (await api.put<Product>(`/productos/${id}`, { disponible })).data,
  remove: async (id: number) => {
    await api.delete(`/productos/${id}`)
  },
}
