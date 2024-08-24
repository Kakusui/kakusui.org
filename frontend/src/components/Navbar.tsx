// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// chakra-ui
import {
    Box,
    Collapse,
    Flex,
    Icon,
    IconButton,
    Image,
    Link,
    Popover,
    PopoverContent,
    PopoverTrigger,
    Stack,
    Text,
    useDisclosure,
} from '@chakra-ui/react';

import {ChevronDownIcon, ChevronRightIcon, CloseIcon, HamburgerIcon,} from '@chakra-ui/icons';

// images
import logo from '../assets/images/kakusui_logo.webp';

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

const DesktopNav = () => 
{
    const linkColor = 'gray.300';
    const linkHoverColor = 'white';
    const popoverContentBgColor = '#14192b';

    return (
        <Stack direction={'row'} spacing={4}>
            {NAV_ITEMS.map((navItem) => (
                <Box key={navItem.label}>
                    <Popover trigger={'hover'} placement={'bottom-start'}>
                        <PopoverTrigger>
                            <Link
                                p={2}
                                href={navItem.href ?? '#'}
                                fontSize={'sm'}
                                fontWeight={500}
                                color={linkColor}
                                _hover={{
                                    textDecoration: 'none',
                                    color: linkHoverColor,
                                }}
                                onClick={(e) => navItem.children && e.preventDefault()}>
                                {navItem.label}
                            </Link>
                        </PopoverTrigger>

                        {navItem.children && (
                            <PopoverContent
                                border={0}
                                boxShadow={'xl'}
                                bg={popoverContentBgColor}
                                p={4}
                                rounded={'xl'}
                                minW={'sm'}>
                                <Stack>
                                    {navItem.children.map((child) => (
                                        <DesktopSubNav key={child.label} {...child} />
                                    ))}
                                </Stack>
                            </PopoverContent>
                        )}
                    </Popover>
                </Box>
            ))}
        </Stack>
    );
};

const DesktopSubNav = ({label, href, subLabel}: NavItem) => 
{
    return (
        <Link
            href={href}
            role={'group'}
            display={'block'}
            p={2}
            rounded={'md'}
            _hover={{bg: 'rgba(255, 255, 255, 0.1)'}}>
            <Stack direction={'row'} align={'center'}>
                <Box>
                    <Text
                        transition={'all .3s ease'}
                        _groupHover={{color: 'orange.400'}}
                        fontWeight={500}>
                        {label}
                    </Text>
                    <Text fontSize={'sm'} color="gray.400">{subLabel}</Text>
                </Box>
                <Flex
                    transition={'all .3s ease'}
                    transform={'translateX(-10px)'}
                    opacity={0}
                    _groupHover={{opacity: '100%', transform: 'translateX(0)'}}
                    justify={'flex-end'}
                    align={'center'}
                    flex={1}>
                    <Icon color={'orange.400'} w={5} h={5} as={ChevronRightIcon}/>
                </Flex>
            </Stack>
        </Link>
    );
};

const MobileNav = () => 
{
    return (
        <Stack
            bg="#14192b"
            p={4}
            display={{md: 'none'}}>
            {NAV_ITEMS.map((navItem) => (
                <MobileNavItem key={navItem.label} {...navItem} />
            ))}
        </Stack>
    );
};

const MobileNavItem = ({label, children, href}: NavItem) => 
{
    const {isOpen, onToggle} = useDisclosure();

    return (
        <Stack spacing={4} onClick={children && onToggle}>
            <Flex
                py={2}
                as={Link}
                href={href ?? '#'}
                justify={'space-between'}
                align={'center'}
                _hover={{
                    textDecoration: 'none',
                }}
                onClick={(e) => children && e.preventDefault()}>
                <Text
                    fontWeight={600}
                    color="gray.300">
                    {label}
                </Text>
                {children && (
                    <Icon
                        as={ChevronDownIcon}
                        transition={'all .25s ease-in-out'}
                        transform={isOpen ? 'rotate(180deg)' : ''}
                        w={6}
                        h={6}
                        color="gray.300"
                    />
                )}
            </Flex>

            <Collapse in={isOpen} animateOpacity style={{marginTop: '0!important'}}>
                <Stack
                    mt={2}
                    pl={4}
                    borderLeft={1}
                    borderStyle={'solid'}
                    borderColor="rgba(255, 255, 255, 0.1)"
                    align={'start'}>
                    {children &&
                        children.map((child) => (
                            <Link key={child.label} py={2} href={child.href} color="gray.400">
                                {child.label}
                            </Link>
                        ))}
                </Stack>
            </Collapse>
        </Stack>
    );
};

interface NavItem 
{
    label: string;
    subLabel?: string;
    children?: Array<NavItem>;
    href?: string;
}

const NAV_ITEMS: Array<NavItem> = 
[
    {
        label: 'Home',
        href: '/home',
    },
    {
        label: 'Products',
        children: [
            {
                label: 'EasyTL',
                subLabel: 'A simple and easy to use custom translator.',
                href: '/easytl',
            },
            {
                label: 'Kairyou',
                subLabel: 'A NER/NLP powered Japanese prepreprocessor.',
                href: '/kairyou',
            },
            {
                label: 'Elucidate',
                subLabel: 'Smarter Translations through LLM Self-Evaluation',
                href: '/elucidate',
            }
        ],
    },
];