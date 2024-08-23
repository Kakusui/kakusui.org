import { useEffect } from 'react';
import {
    Box,
    Button,
    Flex,
    Heading,
    Text,
} from "@chakra-ui/react";
import { Link as RouterLink } from 'react-router-dom';
import { IconBrandGithub } from '@tabler/icons-react';
import landingPageBg from '../assets/images/landing_page.webp';

function LandingPage() {
    useEffect(() => {
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
            </Flex>
        </Box>
    );
}

export default LandingPage;