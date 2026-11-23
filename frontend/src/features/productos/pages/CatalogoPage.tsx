import { useState } from 'react'
import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { productApi } from '../api/productos'
import { categoryApi } from '../../categorias/api/categorias'
import { ProductoCard } from '../components/ProductoCard'
import { Paginacion } from '../../../shared/components/Paginacion'
import { EstadoError, EstadoVacio, Skeleton } from '../../../shared/components/States'

export function CatalogoPage() {
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState<number | undefined>()
  const [page, setPage] = useState(0)
  const categories = useQuery({ queryKey: ['categorias'], queryFn: categoryApi.list })
  const products = useQuery({
    queryKey: ['productos', { search, category, page }],
    queryFn: () =>
      productApi.list({
        search: search || undefined,
        categoria_id: category,
        skip: page * 6,
        limit: 6,
      }),
    placeholderData: keepPreviousData,
  })
  return (
    <>
      <section className="hero">
        <div className="hero-copy">
          <span className="eyebrow">BUENA COMIDA, SIN VUELTAS</span>
          <h1>
            Hoy se come
            <br />
            <em>bien.</em>
          </h1>
          <p>
            Antojos de siempre, hechos como nos gusta.
            <br />
            Elegí tu favorito. Nosotros ponemos el sabor.
          </p>
          <a href="#menu" className="button hero-cta">
            Explorar el menú
          </a>
          <div className="hero-note">
            <span aria-hidden="true">✦</span> Hecho al momento · Para disfrutar en casa
          </div>
        </div>
        <div className="hero-visual">
          <span className="hero-circle" />
          <img src="/images/hero-burger.svg" alt="Hamburguesa artesanal de la casa" />
          <span className="hero-stamp">
            SABOR
            <br />
            <strong>DE CASA</strong>
            <br />
            EN CADA BOCADO
          </span>
        </div>
      </section>
      <section id="menu" className="menu-section">
        <div className="page-heading">
          <div>
            <span className="eyebrow">ELEGÍ ALGO RICO</span>
            <h2>
              Nuestro menú<span className="accent">.</span>
            </h2>
          </div>
          <label className="search-box">
            <span className="sr-only">Buscar productos</span>
            <input
              type="search"
              placeholder="Buscar tu próximo antojo…"
              value={search}
              onChange={(event) => {
                setSearch(event.target.value)
                setPage(0)
              }}
            />
          </label>
        </div>
        {categories.isError && (
          <EstadoError
            error={categories.error}
            retry={() => {
              void categories.refetch()
            }}
          />
        )}
        <div className="category-tabs" aria-label="Filtrar por categoría">
          <button
            className={category === undefined ? 'selected' : ''}
            onClick={() => {
              setCategory(undefined)
              setPage(0)
            }}
          >
            Todo el menú
          </button>
          {categories.data?.map((item) => (
            <button
              key={item.id}
              className={category === item.id ? 'selected' : ''}
              onClick={() => {
                setCategory(item.id)
                setPage(0)
              }}
            >
              {item.nombre}
            </button>
          ))}
        </div>
        {products.isLoading ? (
          <Skeleton cards />
        ) : products.isError ? (
          <EstadoError
            error={products.error}
            retry={() => {
              void products.refetch()
            }}
          />
        ) : !products.data?.items.length ? (
          <EstadoVacio message="No encontramos ese antojo. Probá otra búsqueda." />
        ) : (
          <div
            className={`product-grid ${products.isPlaceholderData ? 'refreshing' : ''}`}
            aria-busy={products.isFetching}
          >
            {products.data.items.map((product) => (
              <ProductoCard key={product.id} product={product} />
            ))}
          </div>
        )}
        <Paginacion page={page} size={6} total={products.data?.total ?? 0} change={setPage} />
      </section>
      <section className="promise">
        <span aria-hidden="true">✦</span>
        <div>
          <h2>De nuestra cocina a tu mesa.</h2>
          <p>Elegí, confirmá y seguí tu pedido desde tu cuenta.</p>
        </div>
        <span className="promise-label">ASÍ DE SIMPLE.</span>
      </section>
    </>
  )
}
