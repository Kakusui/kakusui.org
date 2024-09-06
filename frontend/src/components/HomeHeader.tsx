// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// react
import React, { useState, useEffect } from 'react';
import { jwtDecode } from "jwt-decode";

// chakra-ui
import {
    Box,
    Flex,
    Image,
    Divider,
    Link,
    Text,
} from '@chakra-ui/react';

// logos and images
import logo from '../assets/images/kakusui_logo.webp';

// components
import { DesktopNav } from './NavItems';
import Login from './Login';

const HomeHeader: React.FC = () => 
{
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [userEmail, setUserEmail] = useState<string | null>(null);

    useEffect(() => 
    {
        const token = localStorage.getItem('token');
        if (token) 
        {
            setIsLoggedIn(true);
            try 
            {
                const decoded = jwtDecode(token);
                setUserEmail(decoded.sub as string);
            } 
            catch (error) 
            {
                console.error("Error decoding token:", error);
            }
        } 
        else 
        {
            setIsLoggedIn(false);
            setUserEmail(null);
        }
    }, []);

    const handleLogin = () =>
    {
        setIsLoggedIn(true);
        const token = localStorage.getItem('token');
        if (token) 
        {
            try 
            {
                const decoded = jwtDecode(token);
                setUserEmail(decoded.sub as string);
            } 
            catch (error) 
            {
                console.error("Error decoding token:", error);
            }
        }
    };

    const handleLogout = () =>
    {
        setIsLoggedIn(false);
        setUserEmail(null);
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
                    <Flex align="center">
                        {isLoggedIn && userEmail && (
                            <Text mr={4} fontSize="sm">{userEmail}</Text>
                        )}
                        <Login onLogin={handleLogin} onLogout={handleLogout} />
                    </Flex>
                </Flex>
            </Flex>
            <Divider borderColor="rgba(255, 255, 255, 0.1)" />
        </Box>
    );
};

export default HomeHeader;