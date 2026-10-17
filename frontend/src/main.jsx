import './index.css'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, RouterProvider } from 'react-router'
import { AuthProvider } from './features/auth/AuthProvider.jsx'
import { router } from './app/router.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <RouterProvider router={router} />
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>,
)
