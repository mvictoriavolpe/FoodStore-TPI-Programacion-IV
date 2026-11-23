import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import type { ColumnDef } from '@tanstack/react-table'
import { orderApi } from '../api/pedidos'
import { stateLabels, transitions, type Order, type OrderState } from '../types'
import { DetallePedido } from '../components/DetallePedido'
import { BadgeEstado, dateTime, money } from '../../../shared/ui'
import { DataTable } from '../../../shared/components/DataTable'
import { Paginacion } from '../../../shared/components/Paginacion'
import { EstadoError, Skeleton } from '../../../shared/components/States'

export function AdminPedidosPage() {
  const [filter, setFilter] = useState<OrderState | ''>('')
  const [page, setPage] = useState(0)
  const [detail, setDetail] = useState<number | null>(null)
  const query = useQueryClient()
  const orders = useQuery({
    queryKey: ['pedidos', 'admin', filter, page],
    queryFn: () => orderApi.list(page * 100, 100, filter || undefined),
  })
  const change = useMutation({
    mutationFn: ({ id, state }: { id: number; state: OrderState }) => orderApi.change(id, state),
    onSuccess: () => query.invalidateQueries(),
  })
  const columns: ColumnDef<Order>[] = [
    {
      accessorKey: 'id',
      header: 'Pedido',
      cell: ({ row }) => (
        <button className="text-link" onClick={() => setDetail(row.original.id)}>
          #{row.original.id}
        </button>
      ),
    },
    { accessorKey: 'usuario_id', header: 'Cliente #' },
    {
      accessorKey: 'created_at',
      header: 'Fecha',
      cell: ({ row }) => dateTime(row.original.created_at),
    },
    {
      accessorKey: 'estado',
      header: 'Estado',
      cell: ({ row }) => <BadgeEstado state={row.original.estado} />,
    },
    { accessorKey: 'total', header: 'Total', cell: ({ row }) => money(row.original.total) },
    {
      id: 'actions',
      header: 'Gestionar',
      cell: ({ row }) => (
        <div className="actions">
          <button className="secondary" onClick={() => setDetail(row.original.id)}>
            Detalle
          </button>
          {transitions[row.original.estado].map((state) => (
            <button
              key={state}
              className={state === 'CANCELADO' ? 'danger' : ''}
              disabled={change.isPending}
              onClick={() => {
                if (
                  state !== 'CANCELADO' ||
                  window.confirm(`¿Cancelar el pedido #${row.original.id} y restituir su stock?`)
                )
                  change.mutate({ id: row.original.id, state })
              }}
            >
              {state === 'CANCELADO' ? 'Cancelar' : state === 'ENTREGADO' ? 'Entregar' : 'Preparar'}
            </button>
          ))}
        </div>
      ),
    },
  ]
  return (
    <>
      <div className="section-heading">
        <h2>Pedidos</h2>
        <label>
          Estado
          <select
            value={filter}
            onChange={(event) => {
              setFilter(event.target.value as OrderState | '')
              setPage(0)
            }}
          >
            <option value="">Todos los estados</option>
            {Object.entries(stateLabels).map(([state, label]) => (
              <option key={state} value={state}>
                {label}
              </option>
            ))}
          </select>
        </label>
      </div>
      {change.isError && <EstadoError error={change.error} />}{' '}
      {orders.isLoading ? (
        <Skeleton />
      ) : orders.isError ? (
        <EstadoError
          error={orders.error}
          retry={() => {
            void orders.refetch()
          }}
        />
      ) : (
        <DataTable data={orders.data?.items ?? []} columns={columns} />
      )}{' '}
      {(orders.data?.total ?? 0) > 100 && (
        <Paginacion page={page} size={100} total={orders.data?.total ?? 0} change={setPage} />
      )}{' '}
      {detail !== null && <DetallePedido id={detail} close={() => setDetail(null)} />}
    </>
  )
}
