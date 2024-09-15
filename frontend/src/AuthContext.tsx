// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// react
import React, { createContext, useState, useContext, useEffect } from 'react';

// third-party libraries
import { jwtDecode } from 'jwt-decode';

interface AuthContextType 
{
    isLoggedIn:boolean;
    userEmail:string | null;
    login:(token:string) => void;
    logout:() => void;
    checkLoginStatus:() => Promise<void>;
    isLoading:boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => 
{
    const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);
    const [userEmail, setUserEmail] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);

    const checkLoginStatus = async () => 
    {
        setIsLoading(true);
        const token = localStorage.getItem('token');
        if(token) 
        {
            try 
            {
                const decoded = jwtDecode(token);
                const currentTime = Date.now() / 1000;
                if(decoded.exp && decoded.exp > currentTime) 
                {
                    setIsLoggedIn(true);
                    setUserEmail(decoded.sub as string);
                } 
                else 
                {
                    throw new Error('Token expired');
                }
            } 
            catch (error) 
            {
                console.error('Error verifying token:', error);
                logout();
            }
        } 
        else 
        {
            setIsLoggedIn(false);
            setUserEmail(null);
        }
        setIsLoading(false);
    };

    useEffect(() => 
    {
        checkLoginStatus();
    }, []);

    const login = (token:string) => 
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
        <AuthContext.Provider value={{ isLoggedIn, userEmail, login, logout, checkLoginStatus, isLoading }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => 
{
    const context = useContext(AuthContext);
    if(context === undefined) 
    {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};