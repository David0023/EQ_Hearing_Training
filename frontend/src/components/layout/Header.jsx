import { Link } from "react-router";
import { useAuth } from '../../auth/AuthContext'
import './Header.css'

export function Header() {
    const { logout, isAuthenticated } = useAuth()
    return (
        <header className="header">
            <Link to="/" className="logo">Home</Link>
            <nav className="navbar">
                <Link to="/training">EQ Training</Link>
                <Link to="/about">About</Link>
                {
                    isAuthenticated
                    ? <button onClick={logout}>Log out</button>
                    : <Link to='/login'>Login</Link>
                }
            </nav>
        </header>
    )
}