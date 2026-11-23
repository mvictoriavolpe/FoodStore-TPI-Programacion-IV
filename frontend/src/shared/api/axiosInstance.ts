import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1',
  withCredentials: true,
  timeout: 15000,
})

let onExpired: () => void = () => undefined
export function onSessionExpired(callback: () => void) {
  onExpired = callback
}

api.interceptors.response.use(
  (response) => response,
  (error: unknown) => {
    if (axios.isAxiosError<{ detail?: unknown }>(error)) {
      const url = error.config?.url ?? ''
      const status = error.response?.status
      const authProbe = url === '/auth/token' || url === '/auth/me'
      if (
        (status === 401 && !authProbe) ||
        (status === 400 && error.response?.data.detail === 'Cuenta de usuario desactivada')
      )
        onExpired()
    }
    return Promise.reject(error)
  },
)
