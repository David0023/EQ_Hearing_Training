import { Routes, Route, Link } from 'react-router'
import './App.css'
import { LoginPage } from './pages/LoginPage'
import { SignupPage } from './pages/SignUpPage'
import { ProtectedRoute } from './auth/ProtectedRoute'
import { useAuth } from './auth/AuthContext'
import { Header } from './components/layout/Header'

function HomePage() {
  const { logout, isAuthenticated } = useAuth()

  return (
    <>
      <Header />
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
