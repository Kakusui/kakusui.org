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
    isLoggedIn: boolean;
    userEmail: string | null;
    isPrivilegedUser: boolean;
    credits: number;
    login: () => Promise<void>;
    logout: () => Promise<void>;
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
    const [lastFullCheck, setLastFullCheck] = useState<number>(0);

    const checkTokenExpiration = async () => 
    {
        try {
            const response = await fetch(getURL('/auth/check-token'), {
                method: 'GET',
                credentials: 'include', 
            });
            const data = await response.json();
            return data.valid;
        } catch (error) {
            console.error('Error checking token:', error);
            return false;
        }
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

            return response.ok;
        } 
        catch (error) 
        {
            console.error('Error refreshing access token:', error);
            return false;
        }
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
            if(await checkTokenExpiration()) 
            {
                setIsLoggedIn(true);
            } 
            else 
            {
                const refreshed = await refreshAccessToken();
                if(refreshed) 
                {
                    await performFullCheck();
                    setLastFullCheck(currentTime);
                }
                else 
                {
                    await logout();
                }
            }
        }
        setIsLoading(false);
    };

    const performFullCheck = async () => 
    {
        try 
        {
            // Fetch user info including credits
            const response = await fetch(getURL('/user/info'), 
            {
                method: 'GET',
                credentials: 'include'
            });

            if(response.ok) 
            {
                const data = await response.json();
                setIsLoggedIn(true);
                setUserEmail(data.email);
                setCredits(data.credits); // Set credits
                // backend will verify this too
                setIsPrivilegedUser(data.email === 'kbilyeu@kakusui.org');
            } 
            else 
            {
                throw new Error('Failed to fetch user info');
            }
        } 
        catch (error) 
        {
            console.error('Error fetching user info:', error);
            setIsLoggedIn(false);
            setUserEmail(null);
            setIsPrivilegedUser(false);
            setCredits(0);
        }
    };

    const fetchCsrfToken = async () => {
        try {
            const response = await fetch(getURL('/auth/csrf-token'), {
                method: 'GET',
                credentials: 'include',
            });
            if (response.ok) {
                // The CSRF token is set as a cookie by the server
                console.log('CSRF token fetched successfully');
            } else {
                console.error('Failed to fetch CSRF token');
            }
        } catch (error) {
            console.error('Error fetching CSRF token:', error);
        }
    };

    useEffect(() => 
    {
        fetchCsrfToken();
        checkLoginStatus(true);
    }, []);

    const login = async () => 
    {
        await checkLoginStatus(true);
    };

    const logout = async () => 
    {
        try {
            await fetch(getURL('/auth/logout'), {
                method: 'POST',
                credentials: 'include'
            });
        } catch (error) {
            console.error('Error during logout:', error);
        }
        setIsLoggedIn(false);
        setUserEmail(null);
        setIsPrivilegedUser(false);
        setCredits(0);
        setLastFullCheck(0);
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