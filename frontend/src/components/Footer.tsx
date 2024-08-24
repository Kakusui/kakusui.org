// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// chakra-ui
import { Box, Flex, IconButton, Image, Text } from '@chakra-ui/react';

// icons
import { IconBrandGithub } from '@tabler/icons-react';

// images
import logo from '../assets/images/kakusui_logo.webp';

function Footer() 
{
    return (
        <Box
            bg="#14192b"
            color="gray.300"
            borderTop="1px"
            borderColor="rgba(255, 255, 255, 0.1)"
            boxShadow="0 -1px 2px 0 rgba(0, 0, 0, 0.05)"
            width="100%"
            mt={6}
        >
            <Flex
                maxWidth="container.xl"
                margin="0 auto"
                py={4}
                px={4}
                direction={{ base: 'column', md: 'row' }}
                justify="space-between"
                align="center"
            >
                <Flex display={{ base: 'flex', md: 'none' }} width="100%" justify="space-between" align="center">
                    <IconButton 
                        as='a' 
                        href='https://github.com/Kakusui' 
                        aria-label='Github' 
                        icon={<IconBrandGithub />} 
                        color="white"
                        bg="transparent"
                        _hover={{ bg: 'whiteAlpha.200' }}
                    />
                    <Text textAlign="center">© 2024 Kakusui LLC. All rights reserved</Text>
                    <Image src={logo} boxSize='30px' alt='Kakusui Logo' />
                </Flex>
                <Flex display={{ base: 'none', md: 'flex' }} width="100%" justify="space-between" align="center">
                    <Image src={logo} boxSize='30px' alt='Kakusui Logo' />
                    <Text textAlign="center" flex="1">© 2024 Kakusui LLC. All rights reserved</Text>
                    <IconButton 
                        as='a' 
                        href='https://github.com/Kakusui' 
                        aria-label='Github' 
                        icon={<IconBrandGithub />} 
                        color="white"
                        bg="transparent"
                        _hover={{ bg: 'whiteAlpha.200' }}
                    />
                </Flex>
            </Flex>
        </Box>
    );
}

export default Footer;