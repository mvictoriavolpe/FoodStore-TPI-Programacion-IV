import { useState } from 'react'
import { useForm } from '@tanstack/react-form'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import type { ColumnDef } from '@tanstack/react-table'
import { productApi } from '../api/productos'
import { categoryApi } from '../../categorias/api/categorias'
import type { Product, ProductInput } from '../types'
import { DataTable } from '../../../shared/components/DataTable'
import { Paginacion } from '../../../shared/components/Paginacion'
import { EstadoError, Skeleton } from '../../../shared/components/States'
import { FoodImage, Modal, money } from '../../../shared/ui'

const initial: ProductInput = {
  nombre: '',
  descripcion: '',
  categoria_id: 0,
  precio_base: 0,
  stock: 0,
  disponible: true,
  imagen_url: '',
}

function StockEditor({ product, close }: { product: Product; close: () => void }) {
  const query = useQueryClient()
  const mutation = useMutation({
    mutationFn: ({ stock, disponible }: { stock: number; disponible: boolean }) =>
      productApi.stock(product.id, stock, disponible),
    onSuccess: async () => {
      await query.invalidateQueries()
      close()
    },
  })
  const form = useForm({
    defaultValues: { stock: product.stock, disponible: product.disponible },
    onSubmit: async ({ value }) => {
      try {
        await mutation.mutateAsync(value)
      } catch {
        /* rendered below */
      }
    },
  })
  return (
    <Modal title={`Stock de ${product.nombre}`} close={close}>
      <form
        onSubmit={(event) => {
          event.preventDefault()
          void form.handleSubmit()
        }}
      >
        <form.Field name="stock">
          {(field) => (
            <label>
              Nuevo stock
              <input
                type="number"
                required
                min={0}
                step={1}
                value={Number.isFinite(field.state.value) ? field.state.value : ''}
                onChange={(event) => field.handleChange(event.target.valueAsNumber)}
              />
            </label>
          )}
        </form.Field>
        <form.Field name="disponible">
          {(field) => (
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={field.state.value}
                onChange={(event) => field.handleChange(event.target.checked)}
              />
              Disponible para la venta
            </label>
          )}
        </form.Field>
        <button disabled={mutation.isPending}>
          {mutation.isPending ? 'Guardando…' : 'Actualizar stock'}
        </button>
      </form>
      {mutation.isError && <EstadoError error={mutation.error} />}
    </Modal>
  )
}

export function AdminProductosPage() {
  const [edit, setEdit] = useState<number | null>(null)
  const [stockProduct, setStockProduct] = useState<Product | null>(null)
  const [page, setPage] = useState(0)
  const [notice, setNotice] = useState('')
  const query = useQueryClient()
  const products = useQuery({
    queryKey: ['productos', 'admin', page],
    queryFn: () => productApi.list({ skip: page * 100, limit: 100 }),
  })
  const categories = useQuery({ queryKey: ['categorias'], queryFn: categoryApi.list })
  const save = useMutation({
    mutationFn: ({ data, id }: { data: ProductInput; id: number | null }) =>
      productApi.save(data, id),
    onSuccess: () => query.invalidateQueries(),
  })
  const remove = useMutation({
    mutationFn: productApi.remove,
    onSuccess: () => query.invalidateQueries(),
  })
  const toggle = useMutation({
    mutationFn: (product: Product) => productApi.availability(product.id, !product.disponible),
    onSuccess: () => query.invalidateQueries(),
  })
  const form = useForm({
    defaultValues: initial,
    onSubmit: async ({ value }) => {
      try {
        await save.mutateAsync({ data: value, id: edit })
        setNotice(edit ? 'Producto actualizado.' : 'Producto creado.')
        setEdit(null)
        form.reset(initial)
      } catch {
        /* rendered below */
      }
    },
  })
  const columns: ColumnDef<Product>[] = [
    {
      accessorKey: 'nombre',
      header: 'Producto',
      cell: ({ row }) => (
        <div className="table-product">
          <FoodImage src={row.original.imagen_url} name={row.original.nombre} />
          <div>
            <strong>{row.original.nombre}</strong>
            <small>{row.original.categoria.nombre}</small>
          </div>
        </div>
      ),
    },
    {
      accessorKey: 'precio_base',
      header: 'Precio',
      cell: ({ row }) => money(row.original.precio_base),
    },
    { accessorKey: 'stock', header: 'Stock' },
    {
      accessorKey: 'disponible',
      header: 'Disponible',
      cell: ({ row }) => (
        <button
          className={`badge ${row.original.disponible ? 'entregado' : 'cancelado'}`}
          disabled={toggle.isPending}
          onClick={() => toggle.mutate(row.original)}
        >
          {row.original.disponible ? 'Sí' : 'No'}
        </button>
      ),
    },
    {
      id: 'actions',
      header: 'Acciones',
      cell: ({ row }) => (
        <div className="actions">
          <button
            className="secondary"
            onClick={() => {
              setEdit(row.original.id)
              const product = row.original
              form.setFieldValue('nombre', product.nombre)
              form.setFieldValue('descripcion', product.descripcion)
              form.setFieldValue('categoria_id', product.categoria_id)
              form.setFieldValue('precio_base', product.precio_base)
              form.setFieldValue('stock', product.stock)
              form.setFieldValue('imagen_url', product.imagen_url)
              form.setFieldValue('disponible', product.disponible)
              save.reset()
              setNotice('')
              document.getElementById('product-editor')?.scrollIntoView({ behavior: 'smooth' })
            }}
          >
            Editar
          </button>
          <button className="secondary" onClick={() => setStockProduct(row.original)}>
            Stock
          </button>
          <button
            className="danger"
            disabled={remove.isPending}
            onClick={() => {
              if (window.confirm(`¿Dar de baja ${row.original.nombre}?`)) {
                remove.mutate(row.original.id)
                if (edit === row.original.id) {
                  setEdit(null)
                  form.reset(initial)
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
      <h2>Productos</h2>
      <section className="panel editor-panel" id="product-editor">
        <h3>{edit ? 'Editar producto' : 'Nuevo producto'}</h3>
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
                onChange: ({ value }) => (!value.trim() ? 'Ingresá un nombre' : undefined),
              }}
            >
              {(field) => (
                <label>
                  Nombre
                  <input
                    required
                    value={field.state.value}
                    onChange={(event) => field.handleChange(event.target.value)}
                  />
                </label>
              )}
            </form.Field>
            <form.Field name="categoria_id">
              {(field) => (
                <label>
                  Categoría
                  <select
                    aria-label="Categoría"
                    required
                    value={field.state.value || ''}
                    onChange={(event) => field.handleChange(Number(event.target.value))}
                  >
                    <option value="">Seleccionar categoría</option>
                    {categories.data?.map((category) => (
                      <option key={category.id} value={category.id}>
                        {category.nombre}
                      </option>
                    ))}
                  </select>
                </label>
              )}
            </form.Field>
            <form.Field name="precio_base">
              {(field) => (
                <label>
                  Precio base (ARS)
                  <input
                    required
                    type="number"
                    min={0}
                    step="0.01"
                    value={Number.isFinite(field.state.value) ? field.state.value : ''}
                    onChange={(event) => field.handleChange(event.target.valueAsNumber)}
                  />
                </label>
              )}
            </form.Field>
            <form.Field name="stock">
              {(field) => (
                <label>
                  Stock
                  <input
                    required
                    type="number"
                    min={0}
                    step={1}
                    value={Number.isFinite(field.state.value) ? field.state.value : ''}
                    onChange={(event) => field.handleChange(event.target.valueAsNumber)}
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
            <form.Field name="imagen_url">
              {(field) => (
                <label>
                  Imagen (URL o ruta local)
                  <input
                    placeholder="https://… o /images/burger.svg"
                    value={field.state.value}
                    onChange={(event) => field.handleChange(event.target.value)}
                  />
                </label>
              )}
            </form.Field>
            <form.Field name="disponible">
              {(field) => (
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={field.state.value}
                    onChange={(event) => field.handleChange(event.target.checked)}
                  />
                  Disponible para la venta
                </label>
              )}
            </form.Field>
          </div>
          <div className="actions">
            <button disabled={save.isPending || !categories.data?.length}>
              {save.isPending ? 'Guardando…' : edit ? 'Guardar cambios' : 'Crear producto'}
            </button>
            {edit && (
              <button
                className="secondary"
                type="button"
                onClick={() => {
                  setEdit(null)
                  form.reset(initial)
                  save.reset()
                }}
              >
                Cancelar edición
              </button>
            )}
          </div>
        </form>
        <p className="muted">
          Para editar un producto cuya categoría fue dada de baja, elegí una categoría activa.
        </p>
      </section>
      {notice && (
        <p className="success-box" role="status">
          {notice}
        </p>
      )}
      {categories.isError && <EstadoError error={categories.error} />}{' '}
      {save.isError && <EstadoError error={save.error} />}{' '}
      {remove.isError && <EstadoError error={remove.error} />}{' '}
      {toggle.isError && <EstadoError error={toggle.error} />}{' '}
      {products.isLoading ? (
        <Skeleton />
      ) : products.isError ? (
        <EstadoError
          error={products.error}
          retry={() => {
            void products.refetch()
          }}
        />
      ) : (
        <DataTable data={products.data?.items ?? []} columns={columns} />
      )}{' '}
      {(products.data?.total ?? 0) > 100 && (
        <Paginacion page={page} size={100} total={products.data?.total ?? 0} change={setPage} />
      )}{' '}
      {stockProduct && <StockEditor product={stockProduct} close={() => setStockProduct(null)} />}
    </>
  )
}
