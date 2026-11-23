import { useState } from 'react'
import type { Product } from '../types'
import { useCart } from '../../../store/cartStore'
import { FoodImage, money } from '../../../shared/ui'

export function ProductoCard({ product }: { product: Product }) {
  const add = useCart((state) => state.add)
  const quantity = useCart(
    (state) => state.items.find((item) => item.producto_id === product.id)?.cantidad ?? 0,
  )
  const [added, setAdded] = useState(false)
  const available = product.disponible && product.stock > 0
  return (
    <article className={`product-card ${available ? '' : 'unavailable'}`}>
      <div className="product-image">
        <FoodImage src={product.imagen_url} name={product.nombre} />
        <span className="category-pill">{product.categoria.nombre}</span>
        {!available && <span className="sold-out">Sin disponibilidad</span>}
      </div>
      <div className="product-body">
        <h3>{product.nombre}</h3>
        <p>{product.descripcion || 'Preparado al momento, con ingredientes seleccionados.'}</p>
        <div className="product-bottom">
          <div>
            <strong>{money(product.precio_base)}</strong>
            <small>{product.stock > 0 ? `${product.stock} disponibles` : 'Sin stock'}</small>
          </div>
          <button
            disabled={!available || quantity >= product.stock}
            aria-label={`Agregar ${product.nombre} al carrito`}
            onClick={() => {
              add(product)
              setAdded(true)
            }}
          >
            + Agregar
          </button>
        </div>
        {added && (
          <small className="added-message" role="status">
            En tu carrito: {quantity}
          </small>
        )}
      </div>
    </article>
  )
}
