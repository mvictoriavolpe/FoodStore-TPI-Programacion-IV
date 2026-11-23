import { useQuery } from '@tanstack/react-query'
import { orderApi } from '../api/pedidos'
import { BadgeEstado, dateTime, Modal, money } from '../../../shared/ui'
import { EstadoError, Skeleton } from '../../../shared/components/States'

export function DetallePedido({ id, close }: { id: number; close: () => void }) {
  const order = useQuery({ queryKey: ['pedidos', 'detalle', id], queryFn: () => orderApi.get(id) })
  return (
    <Modal title={`Pedido #${id}`} close={close}>
      {order.isLoading ? (
        <Skeleton />
      ) : order.isError ? (
        <EstadoError error={order.error} />
      ) : (
        order.data && (
          <>
            <BadgeEstado state={order.data.estado} />
            <p>{dateTime(order.data.created_at)}</p>
            <div className="detail-meta">
              <p>
                <strong>Entrega</strong>
                <br />
                {order.data.direccion_entrega}
              </p>
              <p>
                <strong>Pago</strong>
                <br />
                {order.data.forma_pago === 'EFECTIVO' ? 'Efectivo' : 'Transferencia'}
              </p>
            </div>
            {order.data.notas && (
              <p>
                <strong>Notas:</strong> {order.data.notas}
              </p>
            )}
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Producto</th>
                    <th>Cantidad</th>
                    <th>Precio unitario</th>
                    <th>Subtotal</th>
                  </tr>
                </thead>
                <tbody>
                  {order.data.items.map((item) => (
                    <tr key={item.producto_id}>
                      <td>{item.nombre_producto}</td>
                      <td>{item.cantidad}</td>
                      <td>{money(item.precio_unitario)}</td>
                      <td>{money(item.subtotal)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="summary-total">
              <span>Total</span>
              <strong>{money(order.data.total)}</strong>
            </div>
          </>
        )
      )}
    </Modal>
  )
}
