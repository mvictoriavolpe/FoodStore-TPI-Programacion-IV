import { useQuery } from '@tanstack/react-query'
import { orderApi } from '../api/pedidos'
import { money } from '../../../shared/ui'
import { EstadoError, Skeleton } from '../../../shared/components/States'

export function AdminResumenPage() {
  const summary = useQuery({ queryKey: ['resumen'], queryFn: orderApi.summary })
  if (summary.isLoading) return <Skeleton />
  if (summary.isError)
    return (
      <EstadoError
        error={summary.error}
        retry={() => {
          void summary.refetch()
        }}
      />
    )
  const data = summary.data
  if (!data) return null
  return (
    <>
      <div className="section-heading">
        <div>
          <h2>La cocina en números</h2>
          <p>Una vista rápida de cómo va el negocio.</p>
        </div>
        <button
          className="secondary"
          disabled={summary.isFetching}
          onClick={() => {
            void summary.refetch()
          }}
        >
          Actualizar
        </button>
      </div>
      <div className="metrics-grid">
        {[
          ['Pedidos de hoy', data.pedidos_hoy],
          ['Pendientes', data.pendientes],
          ['En preparación', data.en_preparacion],
          ['Entregados', data.entregados],
          ['Cancelados', data.cancelados],
          ['Ingresos entregados', money(data.ingresos_entregados)],
        ].map(([label, value]) => (
          <article className="metric" key={label}>
            <span>{label}</span>
            <strong>{value}</strong>
          </article>
        ))}
      </div>
      <p className="muted">
        Los pedidos de hoy se cuentan según la fecha UTC. Los ingresos incluyen únicamente pedidos
        entregados.
      </p>
    </>
  )
}
