/*
Copyright Kakusui LLC 2024 (https://kakusui.org) (https://github.com/Kakusui)
Use of this source code is governed by a GNU General Public License v3.0
license that can be found in the LICENSE file.
*/

import Router from "./Router.tsx";
import {ChakraProvider, Container} from "@chakra-ui/react";
import Development from "./components/DevelopmentBanner.tsx";
import Navbar from "./components/Navbar.tsx";
import Footer from "./components/Footer.tsx";
import theme from "./theme.ts";


function App() {


    if (import.meta.env.VITE_SHOWDEV === "true") {
        return (
            <ChakraProvider theme={theme}>
                <Development/>
            </ChakraProvider>
        );
    }

    return (
        <ChakraProvider theme={theme}>
            <Navbar/>
            <Container maxW={'6xl'}>
                <Router/>
            </Container>
            <Footer/>
        </ChakraProvider>
    );
}

export default App;