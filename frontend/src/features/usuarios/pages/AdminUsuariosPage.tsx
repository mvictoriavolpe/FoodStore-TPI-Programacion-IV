import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import type { ColumnDef } from '@tanstack/react-table'
import { userApi } from '../api/usuarios'
import type { User } from '../types'
import { useAuth } from '../../../store/authStore'
import { DataTable } from '../../../shared/components/DataTable'
import { EstadoError, Skeleton } from '../../../shared/components/States'

export function AdminUsuariosPage() {
  const me = useAuth((state) => state.user)
  const query = useQueryClient()
  const users = useQuery({ queryKey: ['usuarios'], queryFn: userApi.list })
  const change = useMutation({
    mutationFn: userApi.setDisabled,
    onSuccess: () => query.invalidateQueries({ queryKey: ['usuarios'] }),
  })
  const columns: ColumnDef<User>[] = [
    { accessorKey: 'username', header: 'Usuario' },
    { accessorKey: 'full_name', header: 'Nombre' },
    { accessorKey: 'email', header: 'Email' },
    { accessorKey: 'role', header: 'Rol' },
    {
      id: 'status',
      header: 'Estado',
      cell: ({ row }) => (
        <span className={`badge ${row.original.disabled ? 'cancelado' : 'entregado'}`}>
          {row.original.disabled ? 'Desactivado' : 'Activo'}
        </span>
      ),
    },
    {
      id: 'actions',
      header: 'Acciones',
      cell: ({ row }) =>
        row.original.id === me?.id ? (
          <span className="muted">Tu cuenta</span>
        ) : (
          <button
            className={row.original.disabled ? 'secondary' : 'danger'}
            disabled={change.isPending}
            onClick={() => change.mutate(row.original)}
          >
            {row.original.disabled ? 'Activar' : 'Desactivar'}
          </button>
        ),
    },
  ]
  return (
    <>
      <h2>Usuarios</h2>
      <p>Administrá el acceso de clientes y administradores.</p>
      {change.isError && <EstadoError error={change.error} />}{' '}
      {users.isLoading ? (
        <Skeleton />
      ) : users.isError ? (
        <EstadoError
          error={users.error}
          retry={() => {
            void users.refetch()
          }}
        />
      ) : (
        <DataTable data={users.data ?? []} columns={columns} />
      )}
    </>
  )
}
