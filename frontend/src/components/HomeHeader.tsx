// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// react
import React from 'react';
import { Link as RouterLink } from 'react-router-dom';

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
import { DesktopNav, NAV_ITEMS } from './NavItems';
import Login from './Login';

import { useAuth } from '../contexts/AuthContext';

const HomeHeader: React.FC = () => 
{
    const { isLoggedIn, userEmail, isLoading, isPrivilegedUser } = useAuth();

    const navItems = isPrivilegedUser ? [...NAV_ITEMS, { label: 'Admin', href: '/admin' }] : NAV_ITEMS;

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
                        <DesktopNav items={navItems} />
                    </Flex>
                    <Flex align="center">
                        {!isLoading && isLoggedIn && userEmail && (
                            <Link as={RouterLink} to="/profile" fontSize="sm" fontWeight="medium" color="orange.400" mr={4}>
                                {userEmail}
                            </Link>
                        )}
                        <Login />
                    </Flex>
                </Flex>
            </Flex>
            <Divider borderColor="rgba(255, 255, 255, 0.1)" />
        </Box>
    );
};

export default HomeHeader;