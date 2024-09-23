// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// react
import { useEffect } from 'react';
import { Link as RouterLink } from 'react-router-dom';

// chakra-ui
import { Box, Heading, Text, VStack, List, ListItem, ListIcon, Button, Flex, IconButton } from '@chakra-ui/react';
import { CheckIcon, ArrowBackIcon } from '@chakra-ui/icons';

// images
import landingPageBg from '../assets/images/landing_page.webp';

function PricingPage()
{
    useEffect(() =>
    {
        document.title = 'Kakusui | Pricing';
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
                <Box
                    maxWidth="600px"
                    width="90%"
                    p={8}
                    borderRadius="xl"
                    boxShadow="xl"
                    bg="rgba(20, 25, 43, 0.9)"
                    color="white"
                    position="relative"
                >
                    <IconButton
                        as={RouterLink}
                        to="/home"
                        aria-label="Back to Home"
                        icon={<ArrowBackIcon />}
                        position="absolute"
                        top="20px"
                        left="20px"
                        colorScheme="orange"
                        variant="ghost"
                        size="lg"
                    />
                    <VStack spacing={6} align="stretch">
                        <Heading as="h1" size="2xl" textAlign="center" color="orange.400">
                            Pricing
                        </Heading>
                        
                        <Text fontSize="xl" textAlign="center">
                            Coming Soon
                        </Text>
                        
                        <List spacing={3}>
                            <ListItem>
                                <ListIcon as={CheckIcon} color="green.500" />
                                LLM-agnostic (use with all LLMs)
                            </ListItem>
                            <ListItem>
                                <ListIcon as={CheckIcon} color="green.500" />
                                No hassle of dealing with API keys
                            </ListItem>
                            <ListItem>
                                <ListIcon as={CheckIcon} color="green.500" />
                                Custom LLMs (planned)
                            </ListItem>
                            <ListItem>
                                <ListIcon as={CheckIcon} color="green.500" />
                                Priority support
                            </ListItem>
                        </List>
                        
                        <Button
                            colorScheme="orange"
                            size="lg"
                            isDisabled={true}
                        >
                            Coming Soon
                        </Button>
                        
                        <Text fontSize="sm" textAlign="center">
                            Stay tuned for our upcoming pricing plans!
                        </Text>
                    </VStack>
                </Box>
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

export default PricingPage;