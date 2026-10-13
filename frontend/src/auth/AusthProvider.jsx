import { useEffect, useState } from "react";
import { AuthContext } from "./AuthContext";
import { login as apiLogin, logout as apiLogout, refreshAccessToken } from "../api/auth";
import { setAccessToken } from "../api/client";

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        let active = true;
        refreshAccessToken()
            .then(({ access_token }) => {
                if (active) {
                    setAccessToken(access_token);
                    setIsAuthenticated(true);
                }
            })
            .catch(() => {
                setAccessToken(null);
                if (active) setIsAuthenticated(false);
            })
            .finally(() => {
                if (active) setIsLoading(false);
            });
        // When a function is returned in React for useEffect,
        // React calls it at the cleanup.
        // Here, we set active to false, so when it close, 
        // we no longer update authentication status.
        return () => { active = false; };
    }, []);

    async function login(email, password) {
        const { access_token } = await apiLogin(email, password);
        setAccessToken(access_token);
        setIsAuthenticated(true);
    }

    async function logout() {
        try {
            await apiLogout();
        } finally {
            setAccessToken(null);
            setUser(null);
            setIsAuthenticated(false);
        }
    }

    return (
        <AuthContext.Provider
        value={{ user, isAuthenticated, isLoading, login, logout }}
        >
            {children}
        </AuthContext.Provider>
    );
}
