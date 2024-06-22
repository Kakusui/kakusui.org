/*
Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
Use of this source code is governed by a GNU General Public License v3.0
license that can be found in the LICENSE file.
*/

import Router from "./Router.tsx";
import {ChakraProvider, Container} from "@chakra-ui/react";
import Navbar from "./components/Navbar.tsx";
import Footer from "./components/Footer.tsx";
import theme from "./theme.ts"; 


function App() 
{
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