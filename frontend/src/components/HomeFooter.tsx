// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// react
import React from 'react';

// chakra-ui
import { Box, Flex, IconButton, Image, Text, Divider } from '@chakra-ui/react';

// icons
import { IconBrandGithub } from '@tabler/icons-react';

// logos and images
import logo from '../assets/images/kakusui_logo.webp';

const HomeFooter: React.FC = () => 
{
    return (
        <Box
            position="absolute"
            bottom={0}
            left={0}
            right={0}
            bg="transparent"
            color="white"
            py={4}
            zIndex={1}
        >
            <Divider borderColor="rgba(255, 255, 255, 0.1)" mb={4} />
            <Flex
                maxWidth="container.xl"
                margin="0 auto"
                px={4}
                direction={{ base: 'column', md: 'row' }}
                justify="space-between"
                align="center"
            >
                <Image src={logo} boxSize='30px' alt='Kakusui Logo' mr={{ base: 0, md: 4 }} mb={{ base: 4, md: 0 }} />
                <Text textAlign="center" flex="1" mx={4} mb={{ base: 4, md: 0 }}>© 2024 Kakusui LLC. All rights reserved</Text>
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
        </Box>
    );
};

export default HomeFooter;