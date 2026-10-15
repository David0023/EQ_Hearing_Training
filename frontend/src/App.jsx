import { Routes, Route, Link } from 'react-router'
import './App.css'
import { LoginPage } from './pages/LoginPage'
import { SignupPage } from './pages/SignUpPage'
import { ProtectedRoute } from './auth/ProtectedRoute'
import { useAuth } from './auth/AuthContext'

function HomePage() {
  const { logout, isAuthenticated } = useAuth()

  return (
    <>
      <h1>Home Page</h1>
      {
        isAuthenticated
        ? <button onClick={logout}>Log out</button>
        : <Link to='/login'>Login</Link>
      }
    </>
  )
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/login/signup" element={<SignupPage/>} />
    </Routes>
  )
}

export default App
