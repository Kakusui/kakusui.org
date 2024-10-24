// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// chakra-ui
import {
    Box,
    Collapse,
    Flex,
    IconButton,
    Image,
    useDisclosure,
    Link,
    Text,
} from '@chakra-ui/react';

import { CloseIcon, HamburgerIcon } from '@chakra-ui/icons';

// images
import logo from '../assets/images/kakusui_logo.webp';

// components
import { DesktopNav, MobileNav, NAV_ITEMS } from './NavItems';
import Login from './Login';

import { useAuth } from '../contexts/AuthContext';
import { Link as RouterLink } from 'react-router-dom';

interface NavbarProps 
{
    isHomePage: boolean;
}

export default function Navbar({ isHomePage }: NavbarProps) 
{
    const { isOpen, onToggle } = useDisclosure();
    const { isLoggedIn, userEmail, credits, isPrivilegedUser, isLoading } = useAuth();

    const navItems = isPrivilegedUser ? [...NAV_ITEMS, { label: 'Admin', href: '/admin' }] : NAV_ITEMS;

    const bgColor = isHomePage ? 'transparent' : '#14192b';
    const borderColor = isHomePage ? 'transparent' : 'rgba(255, 255, 255, 0.1)';
    const boxShadow = isHomePage ? 'none' : '0 1px 2px 0 rgba(0, 0, 0, 0.05)';

    return (
        <Box>
            <Flex
                bg={bgColor}
                color="white"
                minH={'60px'}
                py={{base: 2}}
                px={{base: 4}}
                borderBottom="1px"
                borderColor={borderColor}
                boxShadow={boxShadow}
                align={'center'}
                justify={'center'}
                mb={6}
            >
                <Flex
                    width="100%"
                    maxWidth="container.xl"
                    align="center"
                    justify="space-between"
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
                            <Image src={logo} boxSize='30px' alt='Kakusui Logo'/>
                        </Link>
                        <Flex display={{base: 'none', md: 'flex'}} ml={10}>
                            <DesktopNav items={navItems}/>
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
        </Box>
    );
}