// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// react
import React, { createContext, useState, useContext, useEffect } from 'react';

// custom
import { getURL } from '../utils';

interface AuthContextType 
{
    isLoggedIn:boolean;
    userEmail:string | null;
    isPrivilegedUser:boolean;
    login:(access_token:string) => void;
    logout:() => void;
    checkLoginStatus:() => Promise<void>;
    isLoading:boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => 
{
    const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);
    const [userEmail, setUserEmail] = useState<string | null>(null);
    const [isPrivilegedUser, setIsPrivilegedUser] = useState<boolean>(false);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [lastFullCheck, setLastFullCheck] = useState<number>(0);

    const checkTokenExpiration = () => 
    {
        const token = localStorage.getItem('access_token');
        if(token) 
        {
            const payload = JSON.parse(atob(token.split('.')[1]));
            if(payload.exp * 1000 > Date.now()) 
            {
                return true;
            }
        }
        return false;
    };

    const checkLoginStatus = async (forceFullCheck = false) => 
    {
        setIsLoading(true);
        const currentTime = Date.now();
        const twoHours = 2 * 60 * 60 * 1000;

        if(forceFullCheck || currentTime - lastFullCheck > twoHours) 
        {
            await performFullCheck();
            setLastFullCheck(currentTime);
        } 
        else 
        {
            if(checkTokenExpiration()) 
            {
                setIsLoggedIn(true);
            } 
            else 
            {
                await performFullCheck();
                setLastFullCheck(currentTime);
            }
        }
        setIsLoading(false);
    };

    const performFullCheck = async () => 
    {
        const access_token = localStorage.getItem('access_token');
        if(access_token) 
        {
            try 
            {
                const response = await fetch(getURL('/auth/verify-token'), 
                {
                    method: 'POST',
                    headers: 
                    {
                        'Authorization': `Bearer ${access_token}`,
                        'Content-Type': 'application/json'
                    }
                });

                if(response.ok) 
                {
                    const data = await response.json();
                    if(data.valid) 
                    {
                        setIsLoggedIn(true);
                        setUserEmail(data.email);
                        setIsPrivilegedUser(data.email === 'kbilyeu@kakusui.org');
                    } 
                    else 
                    {
                        throw new Error('Token invalid');
                    }
                } 
                else 
                {
                    throw new Error('Failed to verify token');
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
            setIsPrivilegedUser(false);
        }
    };

    useEffect(() => 
    {
        checkLoginStatus(true);
    }, []);

    const login = async (access_token: string) => 
    {
        localStorage.setItem('access_token', access_token);
        await checkLoginStatus(true);
    };

    const logout = async () => 
    {
        localStorage.removeItem('access_token');
        document.cookie = 'refresh_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; secure; HttpOnly';
        setIsLoggedIn(false);
        setUserEmail(null);
        setIsPrivilegedUser(false);
        setLastFullCheck(0);
    };

    return (
        <AuthContext.Provider value={{ isLoggedIn, userEmail, isPrivilegedUser, login, logout, checkLoginStatus, isLoading }}>
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