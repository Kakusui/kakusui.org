// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// react
import { useState } from 'react';

// chakra-ui
import {
    Box,
    Collapse,
    Flex,
    IconButton,
    Image,
    useDisclosure,
    Link,
} from '@chakra-ui/react';

import { CloseIcon, HamburgerIcon } from '@chakra-ui/icons';

// images
import logo from '../assets/images/kakusui_logo.webp';

// components
import { DesktopNav, MobileNav } from './NavItems';
import Login from './Login';

interface NavbarProps 
{
    isHomePage: boolean;
}

export default function Navbar({ isHomePage }: NavbarProps) 
{
    const { isOpen, onToggle } = useDisclosure();
    const [_, setIsLoggedIn] = useState(false);

    const bgColor = isHomePage ? 'transparent' : '#14192b';
    const borderColor = isHomePage ? 'transparent' : 'rgba(255, 255, 255, 0.1)';
    const boxShadow = isHomePage ? 'none' : '0 1px 2px 0 rgba(0, 0, 0, 0.05)';

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
                            <DesktopNav/>
                        </Flex>
                    </Flex>
                    <Login onLogin={handleLogin} onLogout={handleLogout} />
                </Flex>
            </Flex>

            <Collapse in={isOpen} animateOpacity>
                <MobileNav/>
            </Collapse>
        </Box>
    );
}