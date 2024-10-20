// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// chakra-ui
import { Flex, IconButton, Image, Text, Link, HStack, useDisclosure } from '@chakra-ui/react';

// icons
import { IconBrandGithub } from '@tabler/icons-react';

// images
import logo from '../assets/images/kakusui_logo.webp';

// components
import FeedbackModal from './FeedbackModal';

const FooterContent = ({ color = "gray.300" }) => 
{
    const { isOpen, onOpen, onClose } = useDisclosure();

    return (
        <>
            <Flex
                maxWidth="container.xl"
                margin="0 auto"
                py={4}
                px={4}
                direction={{ base: 'column', md: 'row' }}
                justify="space-between"
                align="center"
                color={color}
            >
                <Flex display={{ base: 'flex', md: 'none' }} width="100%" justify="space-between" align="center" flexDirection="column">
                    <Flex width="100%" justify="space-between" align="center" mb={2}>
                        <IconButton 
                            as='a' 
                            href='https://github.com/Kakusui' 
                            aria-label='Github' 
                            icon={<IconBrandGithub />} 
                            color="white"
                            bg="transparent"
                            _hover={{ bg: 'whiteAlpha.200' }}
                        />
                        <Link href="/">
                            <Image src={logo} boxSize='30px' alt='Kakusui Logo' />
                        </Link>
                    </Flex>
                    <Text textAlign="center" mb={2}>© 2024 Kakusui LLC. All rights reserved</Text>
                    <HStack spacing={4} justify="center">
                        <Link href="/tos" fontSize="sm" color="orange.400">Terms of Service</Link>
                        <Link href="/privacy" fontSize="sm" color="orange.400">Privacy Policy</Link>
                        <Link onClick={onOpen} fontSize="sm" color="orange.400">Send Feedback</Link>
                    </HStack>
                </Flex>
                <Flex display={{ base: 'none', md: 'flex' }} width="100%" justify="space-between" align="center">
                    <Link href="/">
                        <Image src={logo} boxSize='30px' alt='Kakusui Logo' />
                    </Link>
                    <Flex direction="column" align="center">
                        <Text textAlign="center">© 2024 Kakusui LLC. All rights reserved</Text>
                        <HStack spacing={4} mt={1}>
                            <Link href="/tos" fontSize="sm" color="orange.400">Terms of Service</Link>
                            <Link href="/privacy" fontSize="sm" color="orange.400">Privacy Policy</Link>
                            <Link onClick={onOpen} fontSize="sm" color="orange.400">Send Feedback</Link>
                        </HStack>
                    </Flex>
                    <IconButton 
                        as='a' 
                        href='https://github.com/Kakusui' 
                        aria-label='Github' 
                        icon={<IconBrandGithub />} 
                        color="white"
                        bg="transparent"
                        _hover={{ bg: 'whiteAlpha.200' }}
                    />
                    <Link href="/">
                        <Image src={logo} boxSize='30px' alt='Kakusui Logo' />
                    </Link>
                </Flex>
                <Text textAlign="center" mb={2}>© 2024 Kakusui LLC. All rights reserved</Text>
                <HStack spacing={4} justify="center">
                    <Link href="/tos" fontSize="sm" color="orange.400">Terms of Service</Link>
                    <Link href="/privacy" fontSize="sm" color="orange.400">Privacy Policy</Link>
                </HStack>
            </Flex>
            <Flex display={{ base: 'none', md: 'flex' }} width="100%" justify="space-between" align="center">
                <Link href="/">
                    <Image src={logo} boxSize='30px' alt='Kakusui Logo' />
                </Link>
                <Flex direction="column" align="center">
                    <Text textAlign="center">© 2024 Kakusui LLC. All rights reserved</Text>
                    <HStack spacing={4} mt={1}>
                        <Link href="/tos" fontSize="sm" color="orange.400">Terms of Service</Link>
                        <Link href="/privacy" fontSize="sm" color="orange.400">Privacy Policy</Link>
                    </HStack>
                </Flex>
            </Flex>
            <FeedbackModal isOpen={isOpen} onClose={onClose} />
        </>
    );
};

export default FooterContent;