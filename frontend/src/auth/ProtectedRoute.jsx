import { Navigate } from 'react-router'
import { useAuth } from './AuthContext'

export function ProtectedRoute({ children }) {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) return <p>Loading…</p>
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return children
}
