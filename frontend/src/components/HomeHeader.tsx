// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// react
import React, { useState } from 'react';

// chakra-ui
import {
    Box,
    Flex,
    Image,
    Divider,
    Link,
} from '@chakra-ui/react';

// logos and images
import logo from '../assets/images/kakusui_logo.webp';

// components
import { DesktopNav } from './NavItems';
import Login from './Login';

const HomeHeader: React.FC = () => 
{
    const [_, setIsLoggedIn] = useState(false);

    const handleLogin = () =>
    {
        setIsLoggedIn(true);
    };

    const handleLogout = () =>
    {
        setIsLoggedIn(false);
        localStorage.removeItem('token');
    };

    return (
        <Box position="absolute" top={0} left={0} right={0} zIndex={1} mb={4}>
            <Flex
                bg="transparent"
                color="white"
                minH={'60px'}
                py={{ base: 2 }}
                px={{ base: 4 }}
                align={'center'}
                justify={'center'}
            >
                <Flex
                    width="100%"
                    maxWidth="container.xl"
                    justify="space-between"
                    align="center"
                >
                    <Flex align="center">
                        <Link href="/">
                            <Image src={logo} boxSize='30px' alt='Kakusui Logo' mr={4}/>
                        </Link>
                        <DesktopNav />
                    </Flex>
                    <Login onLogin={handleLogin} onLogout={handleLogout} />
                </Flex>
            </Flex>
            <Divider borderColor="rgba(255, 255, 255, 0.1)" />
        </Box>
    );
};

export default HomeHeader;