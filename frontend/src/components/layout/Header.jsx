import { Link } from "react-router";
import { useAuth } from '../../features/auth/AuthContext'
import './Header.css'

export function Header() {
    const { logout, isAuthenticated } = useAuth()

    const buttons = (
        isAuthenticated
        ? (
            <>
                <button onClick={logout}>Log out</button>
                <button>Profile</button>
            </>
        )
        : <Link to='/login'>Login</Link>
    )

    return (
        <header className="header">
            <Link to="/" className="logo">Home</Link>
            <nav className="navbar">
                <Link to="/training">EQ Training</Link>
                <Link to="/about">About</Link>
                {buttons}
            </nav>
        </header>
    )
}