// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// react
import React, { createContext, useState, useContext, useEffect, useCallback, useRef } from 'react';

// custom
import { getURL } from '../utils';

interface AuthContextType 
{
    isLoggedIn: boolean;
    userEmail: string | null;
    isPrivilegedUser: boolean;
    credits: number;
    login: (access_token: string) => void;
    logout: () => void;
    checkLoginStatus: (forceFullCheck?: boolean) => Promise<void>;
    isLoading: boolean;
    updateCredits: (newCredits: number) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => 
{
    const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);
    const [userEmail, setUserEmail] = useState<string | null>(null);
    const [isPrivilegedUser, setIsPrivilegedUser] = useState<boolean>(false);
    const [credits, setCredits] = useState<number>(0);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const lastFullCheckRef = useRef<number>(0);

    const checkTokenExpiration = () => 
    {
        const token = localStorage.getItem('access_token');
        if(token) 
        {
            try
            {
                const encodedPayload = token.split('.')[1];
                if(!encodedPayload) return false;

                const normalizedPayload = encodedPayload.replace(/-/g, '+').replace(/_/g, '/');
                const paddedPayload = normalizedPayload.padEnd(
                    normalizedPayload.length + (4 - normalizedPayload.length % 4) % 4,
                    '='
                );
                const payload = JSON.parse(atob(paddedPayload));
                return typeof payload.exp === 'number' && payload.exp * 1000 > Date.now();
            }
            catch
            {
                return false;
            }
        }
        return false;
    };

    const clearAuthState = () =>
    {
        setIsLoggedIn(false);
        setUserEmail(null);
        setIsPrivilegedUser(false);
        setCredits(0);
        lastFullCheckRef.current = 0;
    };

    const refreshAccessToken = async () => 
    {
        try
        {
            const response = await fetch(getURL('/auth/refresh-access-token'), 
            {
                method: 'POST',
                credentials: 'include',
            });

            if(response.ok) 
            {
                const data = await response.json();
                if(data.access_token) 
                {
                    localStorage.setItem('access_token', data.access_token);
                    return true;
                }
            }
            return false;
        } 
        catch (error) 
        {
            console.error('Error refreshing access token:', error);
            return false;
        }
    };

    const performFullCheck = async () => 
    {
        let accessToken = localStorage.getItem('access_token');

        if(!accessToken || !checkTokenExpiration())
        {
            if(!await refreshAccessToken())
            {
                clearAuthState();
                return;
            }
            accessToken = localStorage.getItem('access_token');
        }

        if(!accessToken)
        {
            clearAuthState();
            return;
        }

        try
        {
            const getUserInfo = (token: string) => fetch(getURL('/user/info'),
            {
                method: 'GET',
                headers:
                {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                credentials: 'include'
            });

            let response = await getUserInfo(accessToken);
            if(response.status === 401 && await refreshAccessToken())
            {
                accessToken = localStorage.getItem('access_token');
                if(accessToken) response = await getUserInfo(accessToken);
            }

            if(!response.ok)
            {
                throw new Error('Failed to fetch user info');
            }

            const data = await response.json();
            setIsLoggedIn(true);
            setUserEmail(data.email);
            setCredits(data.credits);
            setIsPrivilegedUser(data.email === 'kbilyeu@kakusui.org');
            lastFullCheckRef.current = Date.now();
        }
        catch (error)
        {
            console.error('Error fetching user info:', error);
            clearAuthState();
        }
    };

    const checkLoginStatus = useCallback(async (forceFullCheck = false) => 
    {
        const currentTime = Date.now();
        const thirtyMinutes = 30 * 60 * 1000;

        if(forceFullCheck || currentTime - lastFullCheckRef.current > thirtyMinutes) 
        {
            setIsLoading(true);
            await performFullCheck();
            setIsLoading(false);
        } 
        else if(!isLoggedIn)
        {
            setIsLoading(true);
            if(checkTokenExpiration()) 
            {
                setIsLoggedIn(true);
            } 
            else 
            {
                const refreshed = await refreshAccessToken();
                if(refreshed) 
                {
                    await performFullCheck();
                }
                else 
                {
                    logout();
                }
            }
            setIsLoading(false);
        }
    }, [isLoggedIn]);

    useEffect(() => 
    {
        checkLoginStatus(true);
    }, []); // Remove checkLoginStatus from the dependency array

    const login = async (access_token: string) => 
    {
        localStorage.setItem('access_token', access_token);
        await checkLoginStatus(true);
    };

    const logout = () => 
    {
        void fetch(getURL('/auth/logout'),
        {
            method: 'POST',
            credentials: 'include',
        }).catch(() => undefined);
        localStorage.removeItem('access_token');
        clearAuthState();
    };

    const updateCredits = (newCredits: number) => 
    {
        setCredits(newCredits);
    };

    return (
        <AuthContext.Provider value={{ isLoggedIn, userEmail, isPrivilegedUser, credits, login, logout, checkLoginStatus, isLoading, updateCredits }}>
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
