// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// react
import { useLocation } from 'react-router-dom';

// chakra-ui
import { ChakraProvider, Box } from "@chakra-ui/react";

// components
import Navbar from "./components/Navbar.tsx";
import Footer from "./components/Footer.tsx";
import PageWrapper from "./components/PageWrapper.tsx";
import theme from "./theme.ts";
import Router from "./Router.tsx";
import { AuthProvider } from './AuthContext';

function App() 
{
    const location = useLocation();
    const isLandingPage = location.pathname === '/';
    const isFullScreenPage = location.pathname === '/home' || location.pathname === '/admin';

    return (
        <ChakraProvider theme={theme}>
            <AuthProvider>
                {!isLandingPage && !isFullScreenPage && <Navbar isHomePage={false} />}
                {isLandingPage || isFullScreenPage ? (
                    <Router />
                ) : (
                    <PageWrapper showBackground={false}>
                        <Box maxWidth="container.xl" margin="0 auto">
                            <Router />
                        </Box>
                    </PageWrapper>
                )}
                {!isLandingPage && !isFullScreenPage && <Footer />}
            </AuthProvider>
        </ChakraProvider>
    );
}

export default App;