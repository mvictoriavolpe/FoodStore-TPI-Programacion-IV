import { Link } from 'react-router-dom'
import { useCart } from '../../../store/cartStore'
import { FoodImage, money } from '../../../shared/ui'
import { EstadoVacio } from '../../../shared/components/States'

export function CarritoPage() {
  const { items, change, remove, clear, total } = useCart()
  return (
    <>
      <div className="page-heading">
        <div>
          <span className="eyebrow">TUS ELEGIDOS</span>
          <h1>
            Tu carrito<span className="accent">.</span>
          </h1>
        </div>
        <Link className="text-link" to="/">
          Seguir eligiendo
        </Link>
      </div>
      {!items.length ? (
        <>
          <EstadoVacio message="Tu carrito espera algo rico." />
          <Link className="button" to="/">
            Ver el menú
          </Link>
        </>
      ) : (
        <div className="checkout-grid">
          <section className="panel">
            {items.map((item) => (
              <div className="cart-row" key={item.producto_id}>
                <FoodImage src={item.imagen_url} name={item.nombre} />
                <div className="cart-description">
                  <h3>{item.nombre}</h3>
                  <p>{money(item.precio_unitario)} por unidad</p>
                  <button
                    className="text-button danger-text"
                    onClick={() => remove(item.producto_id)}
                  >
                    Quitar
                  </button>
                </div>
                <label className="quantity-label">
                  Cantidad
                  <input
                    aria-label={`Cantidad de ${item.nombre}`}
                    type="number"
                    min={1}
                    max={item.stock}
                    step={1}
                    value={item.cantidad}
                    onChange={(event) => change(item.producto_id, event.target.valueAsNumber)}
                  />
                </label>
                <strong>{money(item.precio_unitario * item.cantidad)}</strong>
              </div>
            ))}
            <button
              className="text-button danger-text"
              onClick={() => {
                if (window.confirm('¿Vaciar el carrito?')) clear()
              }}
            >
              Vaciar carrito
            </button>
          </section>
          <aside className="panel order-summary">
            <span className="eyebrow">YA CASI ESTÁ</span>
            <h2>Tu pedido</h2>
            <div className="summary-line">
              <span>Productos</span>
              <span>{items.reduce((sum, item) => sum + item.cantidad, 0)}</span>
            </div>
            <div className="summary-total">
              <span>Total</span>
              <strong>{money(total())}</strong>
            </div>
            <p>Confirmamos el precio y el stock al realizar el pedido.</p>
            <Link className="button block" to="/checkout">
              Continuar al checkout
            </Link>
          </aside>
        </div>
      )}
    </>
  )
}
