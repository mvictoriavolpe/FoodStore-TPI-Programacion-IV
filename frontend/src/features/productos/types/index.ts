import type { Category } from '../../categorias/types'
export interface ProductInput {
  nombre: string
  descripcion: string
  categoria_id: number
  precio_base: number
  stock: number
  disponible: boolean
  imagen_url: string
}
export interface Product extends ProductInput {
  id: number
  activo: boolean
  categoria: Category
}
export interface ProductFilters {
  skip?: number
  limit?: number
  search?: string
  categoria_id?: number
  disponible?: boolean
}
