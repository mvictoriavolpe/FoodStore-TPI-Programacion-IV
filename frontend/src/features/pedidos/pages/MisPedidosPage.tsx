import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { orderApi } from '../api/pedidos'
import { DetallePedido } from '../components/DetallePedido'
import { BadgeEstado, dateTime, money } from '../../../shared/ui'
import { Paginacion } from '../../../shared/components/Paginacion'
import { EstadoError, EstadoVacio, Skeleton } from '../../../shared/components/States'
import { useAuth } from '../../../store/authStore'

export function MisPedidosPage() {
  const [page, setPage] = useState(0)
  const [detail, setDetail] = useState<number | null>(null)
  const user = useAuth((state) => state.user)
  const query = useQueryClient()
  const orders = useQuery({
    queryKey: ['pedidos', user?.id, page],
    queryFn: () => orderApi.list(page * 10, 10),
  })
  const cancel = useMutation({
    mutationFn: orderApi.cancel,
    onSuccess: () => query.invalidateQueries(),
  })
  return (
    <>
      <div className="page-heading">
        <div>
          <span className="eyebrow">DE LA COCINA A TU CASA</span>
          <h1>
            Mis pedidos<span className="accent">.</span>
          </h1>
        </div>
      </div>
      {cancel.isError && <EstadoError error={cancel.error} />}
      <p>
        Consultá el detalle y el estado de tus pedidos. Podés cancelar mientras estén pendientes.
      </p>
      {user?.role === 'admin' && (
        <p className="info-box">
          Tu cuenta de administrador puede ver todos los pedidos. La gestión completa está en el
          panel.
        </p>
      )}
      {orders.isLoading ? (
        <Skeleton />
      ) : orders.isError ? (
        <EstadoError
          error={orders.error}
          retry={() => {
            void orders.refetch()
          }}
        />
      ) : !orders.data?.items.length ? (
        <EstadoVacio message="Todavía no hay pedidos." />
      ) : (
        <div className="orders-list">
          {orders.data.items.map((order) => (
            <article className="panel order-card" key={order.id}>
              <div className="order-card-top">
                <div>
                  <span className="eyebrow">{dateTime(order.created_at)}</span>
                  <h2>Pedido #{order.id}</h2>
                </div>
                <BadgeEstado state={order.estado} />
              </div>
              <p>
                {order.items
                  .map((item) => `${item.cantidad} × ${item.nombre_producto}`)
                  .join(' · ')}
              </p>
              <p>{order.direccion_entrega}</p>
              <div className="order-card-bottom">
                <strong>{money(order.total)}</strong>
                <div className="actions">
                  <button className="secondary" onClick={() => setDetail(order.id)}>
                    Ver detalle
                  </button>
                  {order.estado === 'PENDIENTE' && order.usuario_id === user?.id && (
                    <button
                      className="danger"
                      disabled={cancel.isPending}
                      onClick={() => {
                        if (window.confirm(`¿Cancelar el pedido #${order.id}?`))
                          cancel.mutate(order.id)
                      }}
                    >
                      Cancelar pedido
                    </button>
                  )}
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
      <Paginacion page={page} size={10} total={orders.data?.total ?? 0} change={setPage} />
      {detail !== null && <DetallePedido id={detail} close={() => setDetail(null)} />}
    </>
  )
}
