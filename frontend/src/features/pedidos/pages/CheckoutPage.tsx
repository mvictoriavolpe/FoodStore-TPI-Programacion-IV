import { Link, useNavigate } from 'react-router-dom'
import { useForm } from '@tanstack/react-form'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useCart } from '../../../store/cartStore'
import { orderApi } from '../api/pedidos'
import type { Payment } from '../types'
import { money } from '../../../shared/ui'
import { EstadoError, EstadoVacio } from '../../../shared/components/States'

export function CheckoutPage() {
  const { items, clear, total } = useCart()
  const navigate = useNavigate()
  const query = useQueryClient()
  const mutation = useMutation({
    mutationFn: orderApi.create,
    onSuccess: async () => {
      clear()
      await query.invalidateQueries()
      navigate('/mis-pedidos', { replace: true })
    },
  })
  const form = useForm({
    defaultValues: { direccion_entrega: '', forma_pago: 'EFECTIVO' as Payment, notas: '' },
    onSubmit: async ({ value }) => {
      if (!items.length) return
      try {
        await mutation.mutateAsync({
          ...value,
          items: items.map((item) => ({ producto_id: item.producto_id, cantidad: item.cantidad })),
        })
      } catch {
        /* rendered below */
      }
    },
  })
  if (!items.length)
    return (
      <>
        <EstadoVacio message="Agregá productos antes de confirmar." />
        <Link className="button" to="/">
          Volver al menú
        </Link>
      </>
    )
  return (
    <>
      <div className="page-heading">
        <div>
          <span className="eyebrow">EL ÚLTIMO PASO</span>
          <h1>
            Confirmá tu pedido<span className="accent">.</span>
          </h1>
        </div>
      </div>
      <div className="checkout-grid">
        <section className="panel">
          <h2>¿Dónde lo disfrutás?</h2>
          <form
            onSubmit={(event) => {
              event.preventDefault()
              void form.handleSubmit()
            }}
          >
            <form.Field
              name="direccion_entrega"
              validators={{
                onChange: ({ value }) =>
                  value.trim().length < 5
                    ? 'Ingresá una dirección de 5 a 200 caracteres'
                    : undefined,
              }}
            >
              {(field) => (
                <label>
                  Dirección de entrega
                  <input
                    name="direccion_entrega"
                    autoComplete="street-address"
                    placeholder="Calle, número, piso y departamento"
                    required
                    minLength={5}
                    maxLength={200}
                    value={field.state.value}
                    onBlur={field.handleBlur}
                    onChange={(event) => field.handleChange(event.target.value)}
                  />
                  {field.state.meta.isTouched && (
                    <small className="field-error">{field.state.meta.errors.join(', ')}</small>
                  )}
                </label>
              )}
            </form.Field>
            <form.Field name="forma_pago">
              {(field) => (
                <label>
                  Forma de pago
                  <select
                    name="forma_pago"
                    value={field.state.value}
                    onChange={(event) => field.handleChange(event.target.value as Payment)}
                  >
                    <option value="EFECTIVO">Efectivo</option>
                    <option value="TRANSFERENCIA">Transferencia</option>
                  </select>
                  <small>
                    El pago se coordina con el negocio. No se procesa un cobro en la web.
                  </small>
                </label>
              )}
            </form.Field>
            <form.Field name="notas">
              {(field) => (
                <label>
                  Notas para la cocina <span className="optional">(opcional)</span>
                  <textarea
                    name="notas"
                    rows={3}
                    placeholder="¿Algo que tengamos que saber?"
                    value={field.state.value}
                    onChange={(event) => field.handleChange(event.target.value)}
                  />
                </label>
              )}
            </form.Field>
            <button disabled={mutation.isPending}>
              {mutation.isPending ? 'Confirmando…' : 'Realizar pedido'}
            </button>
          </form>
          {mutation.isError && <EstadoError error={mutation.error} />}
        </section>
        <aside className="panel order-summary">
          <h2>Lo que elegiste</h2>
          {items.map((item) => (
            <div className="summary-line" key={item.producto_id}>
              <span>
                {item.cantidad} × {item.nombre}
              </span>
              <strong>{money(item.precio_unitario * item.cantidad)}</strong>
            </div>
          ))}
          <div className="summary-total">
            <span>Total estimado</span>
            <strong>{money(total())}</strong>
          </div>
          <p>
            El stock y los precios se confirman al finalizar. El pedido se crea completo en una sola
            operación.
          </p>
          <Link className="text-link" to="/carrito">
            Revisar mi carrito
          </Link>
        </aside>
      </div>
    </>
  )
}
