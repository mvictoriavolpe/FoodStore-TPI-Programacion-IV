import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../store/authStore'
import { Skeleton } from '../shared/components/States'

export function ProtectedRoute({ role }: { role?: 'admin' }) {
  const { user, loading } = useAuth()
  const location = useLocation()
  if (loading) return <Skeleton />
  if (!user) return <Navigate to="/login" state={{ from: location.pathname }} replace />
  if (role && user.role !== role) return <Navigate to="/unauthorized" replace />
  return <Outlet />
}
