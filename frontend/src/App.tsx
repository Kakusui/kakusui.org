// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// react
import { useLocation } from 'react-router-dom';
import { useEffect } from 'react';
import { useAuth } from './contexts/AuthContext';

// chakra-ui
import { ChakraProvider, Box } from "@chakra-ui/react";

// components
import Navbar from "./components/Navbar.tsx";
import Footer from "./components/Footer.tsx";
import PageWrapper from "./components/PageWrapper.tsx";
import theme from "./theme.ts";
import Router from "./Router.tsx";

// google oauth
import { GoogleOAuthProvider } from '@react-oauth/google';

function AppContent() 
{
    const location = useLocation();
    const { checkLoginStatus } = useAuth();

    useEffect(() => 
    {
        checkLoginStatus();
    }, [location]);

    const isBorderLessFullScreen = location.pathname === '/' || location.pathname === '/pricing' || location.pathname === '/pricing/credits';
    const isFullScreenPage = location.pathname === '/home' || location.pathname === '/admin';

    return (
        <>
            {!isBorderLessFullScreen && !isFullScreenPage && <Navbar isHomePage={false} />}
            {isBorderLessFullScreen || isFullScreenPage ? (
                <Router />
            ) : (
                <PageWrapper showBackground={false}>
                    <Box maxWidth="container.xl" margin="0 auto">
                        <Router />
                    </Box>
                </PageWrapper>
            )}
            {!isBorderLessFullScreen && !isFullScreenPage && <Footer />}
        </>
    );
}

function App() 
{
    return (
        // This is the Google OAuth client ID for Kakusui's Google API Console project.
        // I should be fine hardcoding this. As it's meant for client-side (right?)
        <GoogleOAuthProvider clientId="951070461527-dhsteb0ro97qrq4d2e7cq2mr9ehichol.apps.googleusercontent.com">
            <ChakraProvider theme={theme}>
                <AppContent />
            </ChakraProvider>
        </GoogleOAuthProvider>
    );
}

export default App;