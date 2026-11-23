import { useState } from 'react'
import { useForm } from '@tanstack/react-form'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import type { ColumnDef } from '@tanstack/react-table'
import { categoryApi } from '../api/categorias'
import type { Category, CategoryInput } from '../types'
import { DataTable } from '../../../shared/components/DataTable'
import { EstadoError, Skeleton } from '../../../shared/components/States'

export function AdminCategoriasPage() {
  const [edit, setEdit] = useState<number | null>(null)
  const [notice, setNotice] = useState('')
  const query = useQueryClient()
  const categories = useQuery({ queryKey: ['categorias'], queryFn: categoryApi.list })
  const save = useMutation({
    mutationFn: ({ data, id }: { data: CategoryInput; id: number | null }) =>
      categoryApi.save(data, id),
    onSuccess: () => query.invalidateQueries(),
  })
  const remove = useMutation({
    mutationFn: categoryApi.remove,
    onSuccess: () => query.invalidateQueries(),
  })
  const form = useForm({
    defaultValues: { nombre: '', descripcion: '' },
    onSubmit: async ({ value }) => {
      try {
        await save.mutateAsync({ data: value, id: edit })
        setNotice(edit ? 'Categoría actualizada.' : 'Categoría creada.')
        setEdit(null)
        form.reset()
      } catch {
        /* rendered below */
      }
    },
  })
  const columns: ColumnDef<Category>[] = [
    { accessorKey: 'nombre', header: 'Nombre' },
    { accessorKey: 'descripcion', header: 'Descripción' },
    {
      id: 'actions',
      header: 'Acciones',
      cell: ({ row }) => (
        <div className="actions">
          <button
            className="secondary"
            onClick={() => {
              setEdit(row.original.id)
              form.setFieldValue('nombre', row.original.nombre)
              form.setFieldValue('descripcion', row.original.descripcion)
              setNotice('')
              save.reset()
            }}
          >
            Editar
          </button>
          <button
            className="danger"
            disabled={remove.isPending}
            onClick={() => {
              if (
                window.confirm(
                  `¿Dar de baja ${row.original.nombre}? Sus productos continuarán visibles.`,
                )
              ) {
                remove.mutate(row.original.id)
                if (edit === row.original.id) {
                  setEdit(null)
                  form.reset()
                }
              }
            }}
          >
            Dar de baja
          </button>
        </div>
      ),
    },
  ]
  return (
    <>
      <h2>Categorías</h2>
      <section className="panel editor-panel">
        <h3>{edit ? 'Editar categoría' : 'Nueva categoría'}</h3>
        <form
          onSubmit={(event) => {
            event.preventDefault()
            void form.handleSubmit()
          }}
        >
          <div className="form-grid">
            <form.Field
              name="nombre"
              validators={{
                onChange: ({ value }) =>
                  value.trim().length < 2 ? 'Ingresá al menos 2 caracteres' : undefined,
              }}
            >
              {(field) => (
                <label>
                  Nombre
                  <input
                    required
                    minLength={2}
                    maxLength={100}
                    value={field.state.value}
                    onChange={(event) => field.handleChange(event.target.value)}
                  />
                </label>
              )}
            </form.Field>
            <form.Field name="descripcion">
              {(field) => (
                <label>
                  Descripción
                  <input
                    value={field.state.value}
                    onChange={(event) => field.handleChange(event.target.value)}
                  />
                </label>
              )}
            </form.Field>
          </div>
          <div className="actions">
            <button disabled={save.isPending}>
              {save.isPending ? 'Guardando…' : edit ? 'Guardar cambios' : 'Crear categoría'}
            </button>
            {edit && (
              <button
                type="button"
                className="secondary"
                onClick={() => {
                  setEdit(null)
                  form.reset()
                  save.reset()
                }}
              >
                Cancelar edición
              </button>
            )}
          </div>
        </form>
      </section>
      {notice && (
        <p role="status" className="success-box">
          {notice}
        </p>
      )}
      {save.isError && <EstadoError error={save.error} />}{' '}
      {remove.isError && <EstadoError error={remove.error} />}{' '}
      {categories.isLoading ? (
        <Skeleton />
      ) : categories.isError ? (
        <EstadoError
          error={categories.error}
          retry={() => {
            void categories.refetch()
          }}
        />
      ) : (
        <DataTable data={categories.data ?? []} columns={columns} />
      )}
    </>
  )
}
