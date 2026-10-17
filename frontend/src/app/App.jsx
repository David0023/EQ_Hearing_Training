import { Routes, Route } from 'react-router'
import './App.css'
import { LoginPage } from '../features/auth/pages/LoginPage'
import { SignupPage } from '../features/auth/pages/SignupPage'
import { ProtectedRoute } from '../features/auth/ProtectedRoute'
import { HomePage } from '../pages/HomePage'
import { TrainingPage } from '../features/training/pages/TrainingPage'
import { NotFoundPage } from '../pages/NotFoundPage'



function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/login/signup" element={<SignupPage/>} />
      <Route path="/training" element={<ProtectedRoute><TrainingPage/></ProtectedRoute>} />
      <Route path="*" element={<NotFoundPage/>}/>
    </Routes>
  )
}

export default App
