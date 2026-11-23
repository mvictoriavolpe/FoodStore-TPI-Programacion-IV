import { api } from '../../../shared/api/axiosInstance'
import type { Page } from '../../../shared/api/types'
import type { Order, OrderInput, OrderState, Summary } from '../types'
export const orderApi = {
  list: async (skip = 0, limit = 20, estado?: OrderState) =>
    (await api.get<Page<Order>>('/pedidos', { params: { skip, limit, estado } })).data,
  get: async (id: number) => (await api.get<Order>(`/pedidos/${id}`)).data,
  create: async (data: OrderInput) => (await api.post<Order>('/pedidos', data)).data,
  change: async (id: number, estado: OrderState) =>
    (await api.patch<Order>(`/pedidos/${id}/estado`, { estado })).data,
  cancel: async (id: number) => (await api.patch<Order>(`/pedidos/${id}/cancelar`)).data,
  summary: async () => (await api.get<Summary>('/pedidos/resumen')).data,
}
