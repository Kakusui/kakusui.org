// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// react
import { useEffect } from 'react';
import { Link as RouterLink } from 'react-router-dom';

// chakra-ui
import { Box, Heading, Text, VStack, Table, Thead, Tbody, Tr, Th, Td, Flex, IconButton } from '@chakra-ui/react';
import { ArrowBackIcon } from '@chakra-ui/icons';

// images
import landingPageBg from '../assets/images/landing_page.webp';

// Define the model costs
const modelCosts = {
    'gpt-3.5-turbo': 0.1,
    'gpt-4': 2.0,
    'gpt-4-turbo': 2.0,
    'gpt-4o': 0.625,
    'gpt-4o-mini': 0.0375,
    'gemini-1.0-pro': 0.1,
    'gemini-1.5-pro': 0.3125,
    'gemini-1.5-flash': 0.01875,
    'claude-3-haiku': 0.075,
    'claude-3-sonnet': 0.9,
    'claude-3-5-sonnet': 0.9,
    'claude-3-opus': 4.5
};

function CharToTokenPage()
{
    useEffect(() =>
    {
        document.title = 'Kakusui | Character to Token Costs';
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
                    maxWidth="800px"
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
                        to="/pricing"
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
                            Credit Pricing Model Key
                        </Heading>
                        
                        <Text fontSize="lg" textAlign="center">
                            Credit costs per character for each model
                        </Text>
                        
                        <Table variant="simple" size="sm">
                            <Thead>
                                <Tr>
                                    <Th color="white">Model</Th>
                                    <Th color="white" isNumeric>Credits per Character</Th>
                                </Tr>
                            </Thead>
                            <Tbody>
                                {Object.entries(modelCosts).map(([model, cost]) => (
                                    <Tr key={model}>
                                        <Td>{model}</Td>
                                        <Td isNumeric>{cost}</Td>
                                    </Tr>
                                ))}
                            </Tbody>
                        </Table>
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

export default CharToTokenPage;
