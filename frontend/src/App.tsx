// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// react
import { useLocation } from 'react-router-dom';

// chakra-ui
import { ChakraProvider, Container } from "@chakra-ui/react";

// components
import Navbar from "./components/Navbar.tsx";
import Footer from "./components/Footer.tsx";
import theme from "./theme.ts";
import Router from "./Router.tsx";

function App() 
{
    const location = useLocation();
    const isLandingPage = location.pathname === '/';

    return (
        <ChakraProvider theme={theme}>
            {!isLandingPage && <Navbar />}
            <Container maxW={isLandingPage ? "100%" : "container.xl"} p={isLandingPage ? 0 : undefined}>
                <Router />
            </Container>
            {!isLandingPage && <Footer />}
        </ChakraProvider>
    );
}

export default App;