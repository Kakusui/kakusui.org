/*
Copyright Kakusui LLC 2024 (https://kakusui.org) (https://github.com/Kakusui)
Use of this source code is governed by a GNU General Public License v3.0
license that can be found in the LICENSE file.
*/

import {Box, Container, Flex, HStack, IconButton, Image, Stack, Text, useColorModeValue,} from '@chakra-ui/react';

import {IconBrandGithub} from '@tabler/icons-react';

import logo from '../assets/images/kakusui_logo.png';

function Footer() {
    return (
        <Box
            bg={useColorModeValue('gray.50', 'gray.900')}
            color={useColorModeValue('gray.700', 'gray.200')}>
            <Container
                as={Stack}
                maxW={'6xl'}
                py={4}
                direction={{base: 'column', md: 'row'}}
                spacing={4}
                justify={{base: 'center', md: 'space-between'}}
                align={{base: 'center', md: 'center'}}>
                <HStack>
                    <Flex flex={{base: 1}} justify={{base: 'center', md: 'start'}}>
                        <Image src={logo} boxSize='30px'/>
                        <Flex display={{base: 'none', md: 'flex'}} ml={10}>
                            <Text>© 2024 Kakusui. All rights reserved</Text>
                        </Flex>
                    </Flex>
                </HStack>
                <IconButton as='a' href='https://github.com/Kakusui' aria-label='Github' icon={<IconBrandGithub/>}/>
            </Container>
        </Box>
    );
}


export default Footer;
