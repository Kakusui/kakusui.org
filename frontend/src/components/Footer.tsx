/*
Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
Use of this source code is governed by an GNU Affero General Public License v3.0
license that can be found in the LICENSE file.
*/

import { Box, Container, Flex, IconButton, Image, Stack, Text, useColorModeValue } from '@chakra-ui/react';
import { IconBrandGithub } from '@tabler/icons-react';
import logo from '../assets/images/kakusui_logo.webp';

function Footer() {
    return (
        <Box
            bg={useColorModeValue('gray.50', 'gray.900')}
            color={useColorModeValue('gray.700', 'gray.200')}
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
                    <IconButton as='a' href='https://github.com/Kakusui' aria-label='Github' icon={<IconBrandGithub />} />
                    <Text textAlign="center">© 2024 Kakusui LLC. All rights reserved</Text>
                    <Image src={logo} boxSize='30px' alt='Kakusui Logo' />
                </Flex>
                <Flex display={{ base: 'none', md: 'flex' }} width="100%" justify="space-between" align="center">
                    <Image src={logo} boxSize='30px' alt='Kakusui Logo' />
                    <Text textAlign="center" flex="1">© 2024 Kakusui LLC. All rights reserved</Text>
                    <IconButton as='a' href='https://github.com/Kakusui' aria-label='Github' icon={<IconBrandGithub />} />
                </Flex>
            </Container>
        </Box>
    );
}

export default Footer;