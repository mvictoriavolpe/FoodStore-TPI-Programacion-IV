import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { Product } from '../features/productos/types'

export interface CartItem {
  producto_id: number
  nombre: string
  precio_unitario: number
  cantidad: number
  stock: number
  imagen_url: string
}
interface CartStore {
  items: CartItem[]
  add: (product: Product) => void
  change: (id: number, quantity: number) => void
  remove: (id: number) => void
  clear: () => void
  total: () => number
}

export const useCart = create<CartStore>()(
  persist(
    (set, get) => ({
      items: [],
      add: (product) =>
        set((state) => {
          if (!product.activo || !product.disponible || product.stock < 1) return state
          const existing = state.items.find((item) => item.producto_id === product.id)
          const item: CartItem = {
            producto_id: product.id,
            nombre: product.nombre,
            precio_unitario: product.precio_base,
            cantidad: Math.min((existing?.cantidad ?? 0) + 1, product.stock),
            stock: product.stock,
            imagen_url: product.imagen_url,
          }
          return {
            items: existing
              ? state.items.map((row) => (row.producto_id === product.id ? item : row))
              : [...state.items, item],
          }
        }),
      change: (id, quantity) =>
        set((state) => ({
          items: state.items.map((item) =>
            item.producto_id === id
              ? {
                  ...item,
                  cantidad: Number.isFinite(quantity)
                    ? Math.max(1, Math.min(Math.trunc(quantity), item.stock))
                    : item.cantidad,
                }
              : item,
          ),
        })),
      remove: (id) =>
        set((state) => ({ items: state.items.filter((item) => item.producto_id !== id) })),
      clear: () => set({ items: [] }),
      total: () => get().items.reduce((sum, item) => sum + item.precio_unitario * item.cantidad, 0),
    }),
    { name: 'food-store-cart', version: 1 },
  ),
)
