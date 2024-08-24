// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// react
import React from 'react';

// chakra-ui
import {
    Box,
    Flex,
    Icon,
    Image,
    Link,
    Popover,
    PopoverContent,
    PopoverTrigger,
    Stack,
    Text,
    Divider,
} from '@chakra-ui/react';
import {ChevronRightIcon } from '@chakra-ui/icons';

// logos and images
import logo from '../assets/images/kakusui_logo.webp';

const HomeHeader: React.FC = () => 
{
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
                    justify="flex-start"
                    align="center"
                >
                    <Image src={logo} boxSize='30px' alt='Kakusui Logo' mr={4}/>
                    <DesktopNav />
                </Flex>
            </Flex>
            <Divider borderColor="rgba(255, 255, 255, 0.1)" />
        </Box>
    );
};

const DesktopNav = () => 
{
    const linkColor = 'white';
    const linkHoverColor = 'orange.400';
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
                            >
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
                                minW={'sm'}
                            >
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

const DesktopSubNav = ({ label, href, subLabel }: NavItem) => 
{
    return (
        <Link
            href={href}
            role={'group'}
            display={'block'}
            p={2}
            rounded={'md'}
            _hover={{ bg: 'rgba(255, 255, 255, 0.1)' }}
        >
            <Stack direction={'row'} align={'center'}>
                <Box>
                    <Text
                        transition={'all .3s ease'}
                        _groupHover={{ color: 'orange.400' }}
                        fontWeight={500}
                    >
                        {label}
                    </Text>
                    <Text fontSize={'sm'} color="gray.400">{subLabel}</Text>
                </Box>
                <Flex
                    transition={'all .3s ease'}
                    transform={'translateX(-10px)'}
                    opacity={0}
                    _groupHover={{ opacity: '100%', transform: 'translateX(0)' }}
                    justify={'flex-end'}
                    align={'center'}
                    flex={1}
                >
                    <Icon color={'orange.400'} w={5} h={5} as={ChevronRightIcon} />
                </Flex>
            </Stack>
        </Link>
    );
};

interface NavItem {
    label: string;
    subLabel?: string;
    children?: Array<NavItem>;
    href?: string;
}

const NAV_ITEMS: Array<NavItem> = [
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

export default HomeHeader;