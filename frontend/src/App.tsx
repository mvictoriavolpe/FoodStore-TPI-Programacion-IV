import { useEffect } from 'react'
import { AppRouter } from './routes/AppRouter'
import { useAuth } from './store/authStore'

export function App() {
  const checkSession = useAuth((state) => state.checkSession)
  useEffect(() => {
    void checkSession()
  }, [checkSession])
  return <AppRouter />
}
