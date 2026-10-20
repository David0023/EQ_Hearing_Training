import { useState } from 'react'
import { Link } from 'react-router'
import { signup } from '../api/auth'
import { Header } from '../../../components/layout/Header'
import './AuthPages.css'


function SignupInput() {
    const [username, setUsername] = useState('')
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [isSigningUp, setIsSigningUp] = useState(false)
    const [message, setMessage] = useState('')
    const [error, setError] = useState('')

    async function trySignup() {
        setMessage('')
        setError('')
        setIsSigningUp(true)
        try {
            await signup(username, email, password)
            setMessage('Account created. You can now log in.')
            setUsername('')
            setEmail('')
            setPassword('')
        } catch (error) {
            setError(error.message || 'Could not create your account.')
        } finally {
            setIsSigningUp(false)
        }
    }

    return (<>
        <input
            className='auth-page__input'
            name='signup-username'
            placeholder='username'
            value={username}
            onChange={(e) => setUsername(e.target.value)}
        />
        <input
            className='auth-page__input'
            name='signup-email'
            placeholder='example@domain.com'
            value={email}
            onChange={(e) => setEmail(e.target.value)}
        />
        <input
            className='auth-page__input'
            name='signup-password'
            type='password'
            placeholder='********'
            value={password}
            onChange={(e) => setPassword(e.target.value)}
        />
        <button
            className='auth-page__submit'
            onClick={trySignup}
            disabled={isSigningUp || !username.trim() || !email.trim() || !password}
        >
            {isSigningUp ? 'Signing Up…' : 'Sign Up'}
        </button>
        {message && <p className='auth-page__notice' role='status'>{message}</p>}
        {error && <p className='auth-page__notice' role='alert'>{error}</p>}
    </>)
}


export function SignupPage() {
    return (
        <>
            <Header/>
            <h2 className='page-title'>Sign Up</h2>
            <div className='auth-page__form'>
                <SignupInput/>
            </div>
            <Link className='auth-page__switch' to='/login'>Login</Link>
        </>
    )
}
