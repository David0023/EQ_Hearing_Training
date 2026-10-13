import { useState } from 'react'
import { useAuth } from '../auth/AuthContext'

export function LoginInput() {
    const { login } = useAuth()
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [loggingIn, setLoggingIn] = useState(false)
    const [message, setMessage] = useState('')
    const [error, setError] = useState('')

    async function tryLogin() {
        setLoggingIn(true)
        setMessage('')
        setError('')
        try {
            await login(email, password)
            setMessage('Logged in successfully.')
        } catch (error) {
            setError(error.response?.data?.detail || error.message || 'Could not log in')
        } finally {
            setLoggingIn(false)
            setPassword('')
        }
    }

    return (<>
        <input
            className='login-input'
            name='login-email'
            placeholder='example@domain.com'
            value={email}
            onChange={(e) => setEmail(e.target.value)}
        />
        <input
            className='login-input'
            name='login-password'
            type='password'
            placeholder='********'
            value={password}
            onChange={(e) => setPassword(e.target.value)}
        />
        <button
            className='login-button'
            onClick={() => tryLogin()}
            disabled={loggingIn || !email.trim() || !password}
        >
            {loggingIn ? "Logging In" : "Log in"}
        </button>
        {message && <p role='status'>{message}</p>}
        {error && <p role='alert'>{error}</p>}
    </>)
}
