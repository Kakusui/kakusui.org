/*
Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
Use of this source code is governed by an GNU Affero General Public License v3.0
license that can be found in the LICENSE file.
*/

import { Box, Container, Flex, IconButton, Image, Stack, Text } from '@chakra-ui/react';
import { IconBrandGithub } from '@tabler/icons-react';
import logo from '../assets/images/kakusui_logo.webp';

function Footer() {
    return (
        <Box
            bg="#14192b"
            color="gray.300"
            borderTop="1px"
            borderColor="rgba(255, 255, 255, 0.1)"
            boxShadow="0 -1px 2px 0 rgba(0, 0, 0, 0.05)"
            width="100%">
            <Container
                as={Stack}
                maxW={'6xl'}
                py={4}
                direction={{ base: 'column', md: 'row' }}
                spacing={4}
                justify={{ base: 'space-between', md: 'space-between' }}
                align={{ base: 'center', md: 'center' }}>
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
            </Container>
        </Box>
    );
}

export default Footer;