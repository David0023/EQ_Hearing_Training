import { Link } from 'react-router'
import { useAuth } from './AuthContext'
import { Header } from '../../components/layout/Header'

export function ProtectedRoute({ children }) {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) return <p>Loading…</p>
  if (!isAuthenticated) 
    return (
      <>
        <Header/>
        <h2>Unauthorized Aceess</h2>
        <Link to="/login" replace>Login Page</Link>
      </>
    )
  return children
}
