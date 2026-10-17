import { createBrowserRouter } from "react-router";
import { HomePage } from "../pages/HomePage";
import { LoginPage } from "../features/auth/pages/LoginPage";
import { SignupPage } from "../features/auth/pages/SignupPage";
import { ProtectedRoute } from "../features/auth/ProtectedRoute";
import { NotFoundPage } from "../pages/NotFoundPage";


export const router = createBrowserRouter([
    {
        path: "/",
        element: <HomePage/>
    },
    {
        path: "/login",
        element: <LoginPage/>
    },
    {
        path: "/signup",
        element: <SignupPage/>
    },
    {
        element: <ProtectedRoute/>,
        children: [
            {
                path: "/me",
                element: <></>
            }
        ]
    },
    {
        path: "*",
        element: <NotFoundPage/>
    }
])