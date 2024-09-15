// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

import React, { createContext, useState, useContext, useEffect } from 'react';
import { jwtDecode } from "jwt-decode";
import { getURL } from '../utils';

interface AuthContextType 
{
    isLoggedIn: boolean;
    userEmail: string | null;
    login: (token: string) => void;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => 
{
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [userEmail, setUserEmail] = useState<string | null>(null);

    useEffect(() => 
    {
        const checkLoginStatus = async () => 
        {
            const token = localStorage.getItem('token');
            if (token) 
            {
                try 
                {
                    const response = await fetch(getURL('/verify-token'), 
                    {
                        method: 'POST',
                        headers: 
                        {
                            'Authorization': `Bearer ${token}`
                        }
                    });

                    if (response.ok) 
                    {
                        const data = await response.json();
                        if (data.valid) 
                        {
                            const decoded = jwtDecode(token);
                            setIsLoggedIn(true);
                            setUserEmail(decoded.sub as string);
                        } 
                        else 
                        {
                            throw new Error('Token verification failed');
                        }
                    } 
                    else 
                    {
                        throw new Error('Token verification failed');
                    }
                } 
                catch (error) 
                {
                    console.error("Error verifying token:", error);
                    logout();
                }
            }
        };

        checkLoginStatus();
    }, []);

    const login = (token: string) => 
    {
        localStorage.setItem('token', token);
        const decoded = jwtDecode(token);
        setIsLoggedIn(true);
        setUserEmail(decoded.sub as string);
    };

    const logout = () => 
    {
        localStorage.removeItem('token');
        document.cookie = 'refresh_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; secure; HttpOnly';
        setIsLoggedIn(false);
        setUserEmail(null);
    };

    return (
        <AuthContext.Provider value={{ isLoggedIn, userEmail, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => 
{
    const context = useContext(AuthContext);
    if (context === undefined) 
    {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};