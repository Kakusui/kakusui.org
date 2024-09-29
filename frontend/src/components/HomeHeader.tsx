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
    Text,
    IconButton,
    useDisclosure,
    Collapse,
} from '@chakra-ui/react';

import { CloseIcon, HamburgerIcon } from '@chakra-ui/icons';

// logos and images
import logo from '../assets/images/kakusui_logo.webp';

// components
import { DesktopNav, MobileNav, NAV_ITEMS } from './NavItems';
import Login from './Login';

import { useAuth } from '../contexts/AuthContext';

const HomeHeader: React.FC = () => 
{
    const { isOpen, onToggle } = useDisclosure();
    const { isLoggedIn, userEmail, credits, isLoading, isPrivilegedUser } = useAuth();

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
                        <Flex
                            display={{base: 'flex', md: 'none'}}
                            mr={2}
                        >
                            <IconButton
                                onClick={onToggle}
                                icon={
                                    isOpen ? <CloseIcon w={3} h={3}/> : <HamburgerIcon w={5} h={5}/>
                                }
                                variant={'ghost'}
                                aria-label={'Toggle Navigation'}
                                color="white"
                            />
                        </Flex>
                        <Link href="/">
                            <Image src={logo} boxSize='30px' alt='Kakusui Logo' mr={4}/>
                        </Link>
                        <Flex display={{base: 'none', md: 'flex'}}>
                            <DesktopNav items={navItems} />
                        </Flex>
                    </Flex>
                    <Flex align="center">
                        {!isLoading && isLoggedIn && userEmail && (
                            <Flex align="center">
                                <Text fontSize="sm" fontWeight="medium" mr={2}>{credits} Credits</Text>
                                <Link as={RouterLink} to="/profile" fontSize="sm" fontWeight="medium" color="orange.400" mr={4}>
                                    {userEmail}
                                </Link>
                            </Flex>
                        )}
                        <Login />
                    </Flex>
                </Flex>
            </Flex>
            <Collapse in={isOpen} animateOpacity>
                <MobileNav items={navItems}/>
            </Collapse>
            <Divider borderColor="rgba(255, 255, 255, 0.1)" />
        </Box>
    );
};

export default HomeHeader;