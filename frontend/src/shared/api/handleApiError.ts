import axios from 'axios'

export function handleApiError(error: unknown): string {
  if (axios.isAxiosError<{ detail?: unknown }>(error)) {
    if (!error.response)
      return 'No pudimos conectar con Food Store. Verificá tu conexión y que el backend esté iniciado.'
    const detail = error.response.data.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail))
      return 'Revisá los campos: hay datos incompletos o fuera del rango permitido.'
    return `No pudimos completar la operación (${error.response.status}).`
  }
  return error instanceof Error ? error.message : 'Ocurrió un error inesperado.'
}
