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
} from '@chakra-ui/react';

import { CloseIcon, HamburgerIcon } from '@chakra-ui/icons';

// images
import logo from '../assets/images/kakusui_logo.webp';

// components
import { DesktopNav, MobileNav } from './NavItems';

interface NavbarProps 
{
    isHomePage: boolean;
}

export default function Navbar({ isHomePage }: NavbarProps) 
{
    const {isOpen, onToggle} = useDisclosure();

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
                    <Flex
                        flex={{base: 1, md: 'auto'}}
                        ml={{base: -2}}
                        display={{base: 'flex', md: 'none'}}
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
                    <Flex flex={{base: 1}} justify={{base: 'center', md: 'start'}} align="center">
                        <Image src={logo} boxSize='30px' alt='Kakusui Logo'/>
                        <Flex display={{base: 'none', md: 'flex'}} ml={10}>
                            <DesktopNav/>
                        </Flex>
                    </Flex>
                </Flex>
            </Flex>

            <Collapse in={isOpen} animateOpacity>
                <MobileNav/>
            </Collapse>
        </Box>
    );
}