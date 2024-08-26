// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// react
import { useEffect } from 'react';
import { Link as RouterLink } from 'react-router-dom';

// chakra-ui
import { Box, Button, Flex, Heading, Text } from "@chakra-ui/react";

// icons
import { IconBrandGithub } from '@tabler/icons-react';

// images
import landingPageBg from '../assets/images/landing_page.webp';

function LandingPage() 
{
    useEffect(() => 
    {
        document.title = 'Welcome to Kakusui';
    }, []);

    return (
        <Box
            height="100vh"
            width="100vw"
            position="relative"
            overflow="hidden"
        >
            <Box
                position="absolute"
                top="0"
                left="0"
                right="0"
                bottom="0"
                backgroundImage={`url(${landingPageBg})`}
                backgroundSize="cover"
                backgroundPosition="center"
                filter="brightness(0.6)"
            />
            <Flex
                position="relative"
                height="100%"
                alignItems="center"
                justifyContent="center"
                flexDirection="column"
            >
                <Flex
                    direction="column"
                    align="center"
                    justify="center"
                    textAlign="center"
                    color="white"
                    bg="rgba(20, 25, 43, 0.9)"
                    p={8}
                    borderRadius="xl"
                    maxWidth="500px"
                    width="90%"
                >
                    <Heading size="2xl" color="orange.400" mb={4}>Kakusui</Heading>
                    <Text fontSize="lg" mb={6}>
                        Innovating in language translation using AI, LLMs, and new machine translation technologies.
                    </Text>
                    <Flex direction={{ base: 'column', sm: 'row' }} gap={4}>
                        <Button
                            as={RouterLink}
                            to="/home"
                            colorScheme="orange"
                            size="lg"
                        >
                            Products
                        </Button>
                        <Button
                            as="a"
                            href="https://github.com/Kakusui"
                            target="_blank"
                            rel="noopener noreferrer"
                            leftIcon={<IconBrandGithub />}
                            variant="outline"
                            size="lg"
                            _hover={{ bg: 'whiteAlpha.200' }}
                        >
                            GitHub
                        </Button>
                    </Flex>
                </Flex>
                <Text
                    position="absolute"
                    bottom="6"
                    left="0"
                    right="0"
                    textAlign="center"
                    color="white"
                    fontSize="sm"
                >
                    © Copyright 2024 Kakusui LLC
                </Text>
            </Flex>
        </Box>
    );
}

export default LandingPage;