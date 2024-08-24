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

function App() 
{
    const location = useLocation();
    const isLandingPage = location.pathname === '/';
    const isHomePage = location.pathname === '/home';

    return (
        <ChakraProvider theme={theme}>
            {!isLandingPage && !isHomePage && <Navbar isHomePage={isHomePage} />}
            {isLandingPage ? (
                <Router />
            ) : (
                <PageWrapper showBackground={isHomePage}>
                    <Box maxWidth={isHomePage ? "100%" : "container.xl"} margin="0 auto">
                        <Router />
                    </Box>
                </PageWrapper>
            )}
            {!isLandingPage && !isHomePage && <Footer />}
        </ChakraProvider>
    );
}

export default App;