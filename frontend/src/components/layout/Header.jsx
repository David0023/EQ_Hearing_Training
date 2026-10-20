import { Link } from "react-router";
import { useAuth } from '../../features/auth/AuthContext'
import './Header.css'

export function Header() {
    const { logout, isAuthenticated } = useAuth()

    const buttons = (
        isAuthenticated
        ? (
            <>
                <button className="site-header__button" onClick={logout}>Log out</button>
                <button className="site-header__button">Profile</button>
            </>
        )
        : <Link to='/login'>Login</Link>
    )

    return (
        <header className="site-header">
            <Link to="/" className="site-header__logo">Home</Link>
            <nav className="site-header__nav">
                <Link to="/training">EQ Training</Link>
                <Link to="/about">About</Link>
                {buttons}
            </nav>
        </header>
    )
}
