export type OrderState = 'PENDIENTE' | 'EN_PREPARACION' | 'ENTREGADO' | 'CANCELADO'
export type Payment = 'EFECTIVO' | 'TRANSFERENCIA'
export interface OrderItem {
  producto_id: number
  nombre_producto: string
  cantidad: number
  precio_unitario: number
  subtotal: number
}
export interface Order {
  id: number
  usuario_id: number
  estado: OrderState
  total: number
  forma_pago: Payment
  direccion_entrega: string
  notas: string
  created_at: string
  updated_at: string
  items: OrderItem[]
}
export interface OrderInput {
  items: { producto_id: number; cantidad: number }[]
  forma_pago: Payment
  direccion_entrega: string
  notas: string
}
export interface Summary {
  pendientes: number
  en_preparacion: number
  entregados: number
  cancelados: number
  pedidos_hoy: number
  ingresos_entregados: number
}
export const stateLabels: Record<OrderState, string> = {
  PENDIENTE: 'Pendiente',
  EN_PREPARACION: 'En preparación',
  ENTREGADO: 'Entregado',
  CANCELADO: 'Cancelado',
}
export const transitions: Record<OrderState, OrderState[]> = {
  PENDIENTE: ['EN_PREPARACION', 'CANCELADO'],
  EN_PREPARACION: ['ENTREGADO', 'CANCELADO'],
  ENTREGADO: [],
  CANCELADO: [],
}
