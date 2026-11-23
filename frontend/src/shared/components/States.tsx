import { handleApiError } from '../api/handleApiError'
export function EstadoError({ error, retry }: { error: unknown; retry?: () => void }) {
  return (
    <div className="error-box" role="alert">
      <p>{handleApiError(error)}</p>
      {retry && (
        <button className="secondary" onClick={retry}>
          Reintentar
        </button>
      )}
    </div>
  )
}
export function EstadoVacio({ message = 'Todavía no hay resultados.' }: { message?: string }) {
  return (
    <div className="empty-state">
      <span aria-hidden="true">✦</span>
      <h3>{message}</h3>
      <p>Cuando haya novedades, las vas a encontrar acá.</p>
    </div>
  )
}
export function Skeleton({ cards = false }: { cards?: boolean }) {
  return (
    <div aria-label="Cargando" role="status" className={cards ? 'product-grid' : ''}>
      {Array.from({ length: cards ? 6 : 1 }, (_, index) => (
        <div className="skeleton" key={index} />
      ))}
    </div>
  )
}
