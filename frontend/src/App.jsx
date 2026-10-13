import { Routes, Route } from 'react-router'
import './App.css'
import { LoginInput } from './components/LoginInput'
import { SignupInput } from './components/SignUpInput'
import { ProtectedRoute } from './auth/ProtectedRoute'
import { useAuth } from './auth/AuthContext'

function HomePage() {
  const { logout } = useAuth()

  return (
    <>
      <h1>Home Page</h1>
      <button onClick={logout}>Log out</button>
    </>
  )
}

function App() {
  return (
    <Routes>
      <Route index element={<ProtectedRoute><HomePage /></ProtectedRoute>} />
      <Route path="login" element={<LoginInput />} />
      <Route path="signup" element={<SignupInput/>} />
    </Routes>
  )
}

export default App
