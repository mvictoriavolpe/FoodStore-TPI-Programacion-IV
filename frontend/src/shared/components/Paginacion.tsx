export function Paginacion({
  page,
  total,
  size,
  change,
}: {
  page: number
  total: number
  size: number
  change: (page: number) => void
}) {
  const pages = Math.max(1, Math.ceil(total / size))
  return (
    <div className="pagination">
      <button className="secondary" disabled={page === 0} onClick={() => change(page - 1)}>
        Anterior
      </button>
      <span>
        Página {page + 1} de {pages} · {total} resultados
      </span>
      <button className="secondary" disabled={page + 1 >= pages} onClick={() => change(page + 1)}>
        Siguiente
      </button>
    </div>
  )
}
