import { useState } from 'react'
import { Link, useNavigate } from 'react-router'
import { useAuth } from '../AuthContext'
import { Header } from '../../../components/layout/Header'
import './AuthPages.css'

function LoginInput() {
    const { login } = useAuth()
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [loggingIn, setLoggingIn] = useState(false)
    const [message, setMessage] = useState('')
    const [error, setError] = useState('')
    const navigate = useNavigate()

    async function tryLogin() {
        setLoggingIn(true)
        setMessage('')
        setError('')
        try {
            await login(email, password)
            setMessage('Logged in successfully.')
            navigate('/')
        } catch (error) {
            setError(error.response?.data?.detail || error.message || 'Could not log in')
        } finally {
            setLoggingIn(false)
            setPassword('')
        }
    }

    return (<>
        <input
            className='auth-page__input'
            name='login-email'
            placeholder='example@domain.com'
            value={email}
            onChange={(e) => setEmail(e.target.value)}
        />
        <input
            className='auth-page__input'
            name='login-password'
            type='password'
            placeholder='********'
            value={password}
            onChange={(e) => setPassword(e.target.value)}
        />
        <button
            className='auth-page__submit'
            onClick={() => tryLogin()}
            disabled={loggingIn || !email.trim() || !password}
        >
            {loggingIn ? "Logging In" : "Log in"}
        </button>
        {message && <p className='auth-page__notice' role='status'>{message}</p>}
        {error && <p className='auth-page__notice' role='alert'>{error}</p>}
    </>)
}

export function LoginPage() {
    return (
        <>
            <Header/>
            <h2 className='page-title'>Login</h2>
            <div className='auth-page__form'>
                <LoginInput/>
            </div>
            <Link className='auth-page__switch' to='/signup'>Sign Up</Link>
        </>
    )
}
