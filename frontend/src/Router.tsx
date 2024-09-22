// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// react
import { Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { ReactNode } from 'react';

// chakra-ui
import { Spinner, Center } from "@chakra-ui/react";

// pages
import HomePage from "./pages/HomePage.tsx";

import LandingPage from "./pages/LandingPage.tsx";

import ElucidatePage from './pages/ElucidatePage.tsx';
import ElucidateTermsOfServicePage from './pages/elucidate_mds/ElucidateTosPage.tsx';
import ElucidatePrivacyPolicyPage from './pages/elucidate_mds/ElucidatePrivacyPolicyPage.tsx';
import ElucidateLicensePage from './pages/elucidate_mds/ElucidateLicensePage.tsx';

import EasyTLPage from './pages/EasyTLPage.tsx';
import EasyTLTermsOfServicePage from './pages/easytl_mds/EasyTLTosPage.tsx';
import EasyTLPrivacyPolicyPage from './pages/easytl_mds/EasyTLPrivacyPolicyPage.tsx';
import EasyTLLicensePage from './pages/easytl_mds/EasyTLLicensePage.tsx';

import KairyouPage from "./pages/KairyouPage.tsx";
import KairyouTermsOfServicePage from './pages/kairyou_mds/KairyouTosPage.tsx';
import KairyouPrivacyPolicyPage from './pages/kairyou_mds/KairyouPrivacyPolicyPage.tsx';
import KairyouLicensePage from './pages/kairyou_mds/KairyouLicensePage.tsx';

import NotFoundPage from './pages/error_pages/404.tsx';
import ForbiddenPage from './pages/error_pages/403.tsx';
import InternalErrorPage from './pages/error_pages/500.tsx';

import AdminPanel from './pages/AdminPanel.tsx';

// auth
import { useAuth } from './contexts/AuthContext';

// util
import { getURL } from './utils';

import TosPage from './pages/TosPage.tsx';

import PrivacyPolicyPage from './pages/PrivacyPolicyPage.tsx';

const ProtectedAdminRoute = ({ children }: { children: ReactNode }) => 
{
    const { isLoggedIn, isLoading } = useAuth();
    const [isAdmin, setIsAdmin] = useState<boolean | null>(null);

    useEffect(() => {
        const checkAdminStatus = async () => 
        {
            if (isLoading) 
            {
                return;
            }

            if (isLoggedIn) 
            {
                try 
                {
                    const response = await fetch(getURL('/auth/check-if-admin-user'), 
                    {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                        },
                    });
                    if (response.ok) 
                    {
                        const data = await response.json();
                        setIsAdmin(data.result);
                    } 
                    else 
                    {
                        setIsAdmin(false);
                    }
                } 
                catch (error) 
                {
                    setIsAdmin(false);
                }
            } 
            else 
            {
                setIsAdmin(false);
            }
        };

        checkAdminStatus();
    }, [isLoggedIn, isLoading]);

    if (isLoading || isAdmin === null) 
    {
        return (
            <Center height="100vh">
                <Spinner 
                    thickness="4px"
                    speed="0.65s"
                    emptyColor="gray.200"
                    color="orange.500"
                    size="xl"
                />
            </Center>
        );
    }

    if (!isLoggedIn || !isAdmin) 
    {
        return <Navigate to="/403" replace />;
    }

    return <>{children}</>;
};

function Router() 
{
    return (
        <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/home" element={<HomePage />} />
            <Route path="/elucidate" element={<ElucidatePage />} />
            <Route path="/elucidate/tos" element={<ElucidateTermsOfServicePage />} />
            <Route path="/elucidate/privacy" element={<ElucidatePrivacyPolicyPage />} />
            <Route path="/elucidate/license" element={<ElucidateLicensePage />} />
            <Route path="/easytl" element={<EasyTLPage />} />
            <Route path="/easytl/tos" element={<EasyTLTermsOfServicePage />} />
            <Route path="/easytl/privacy" element={<EasyTLPrivacyPolicyPage />} />
            <Route path="/easytl/license" element={<EasyTLLicensePage />} />
            <Route path="/kairyou" element={<KairyouPage />} />
            <Route path="/kairyou/tos" element={<KairyouTermsOfServicePage />} />
            <Route path="/kairyou/privacy" element={<KairyouPrivacyPolicyPage />} />
            <Route path="/kairyou/license" element={<KairyouLicensePage />} />
            <Route path="/404" element={<NotFoundPage />} />
            <Route path="/403" element={<ForbiddenPage />} />
            <Route path="/500" element={<InternalErrorPage />} />
            <Route path="*" element={<NotFoundPage />} />
            <Route 
                path="/admin" 
                element={
                    <ProtectedAdminRoute>
                        <AdminPanel />
                    </ProtectedAdminRoute>
                } 
            />
            <Route path="/tos" element={<TosPage />} />
            <Route path="/privacy" element={<PrivacyPolicyPage />} />
        </Routes>
    );
}

export default Router;