// import React, { createContext, useContext, useState } from 'react';

// const AuthContext = createContext();

// export function AuthProvider({ children }) {
//     const [isLoggedIn, setIsLoggedIn] = useState(false);

//     return (
//         <AuthContext.Provider value={{ isLoggedIn, setIsLoggedIn }}>
//             {children}
//         </AuthContext.Provider>
//     );
// }

// export function useAuth() {
//     return useContext(AuthContext);
// }

// src/components/AuthContext.js
import React, { createContext, useContext, useState } from 'react';

const AuthContext = createContext();

export function AuthProvider({ children }) {
    const [authToken, setAuthToken] = useState(localStorage.getItem("token") || null);

    const login = (token) => {
        localStorage.setItem("token", token);
        setAuthToken(token);
    };

    const logout = () => {
        localStorage.removeItem("token");
        setAuthToken(null);
    };

    return (
        <AuthContext.Provider value={{ authToken, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    return useContext(AuthContext);
}
