// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// react
import { useState, useEffect } from 'react';
import { Link as RouterLink } from 'react-router-dom';

// chakra-ui
import { Box, Button, Flex, Heading, Text, Input, useToast, Modal, ModalOverlay, ModalContent, ModalHeader, ModalFooter, ModalBody, ModalCloseButton } from "@chakra-ui/react";

// icons
import { IconBrandGithub } from '@tabler/icons-react';

// images
import landingPageBg from '../assets/images/landing_page.webp';

// util
import { getURL } from '../utils';

function LandingPage()
{
    const [email, setEmail] = useState('');
    const [verificationCode, setVerificationCode] = useState('');
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isVerificationStep, setIsVerificationStep] = useState(false);
    const [clientId, setClientId] = useState('');
    const toast = useToast();

    useEffect(() =>
    {
        document.title = 'Welcome to Kakusui';
        
        let storedClientId = localStorage.getItem('kakusui_client_id');
        if(!storedClientId)
        {
            storedClientId = generateClientId();
            localStorage.setItem('kakusui_client_id', storedClientId);
        }
        setClientId(storedClientId);
    }, []);

    const generateClientId = () =>
    {
        const array = new Uint8Array(16);
        crypto.getRandomValues(array);
        return Array.from(array, (byte) => byte.toString(16).padStart(2, '0')).join('');
    };

    const handleSubscribeClick = () =>
    {
        setIsModalOpen(true);
        setIsVerificationStep(false);
    };

    const handleEmailSubmit = async () =>
    {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if(!email || !emailRegex.test(email)) 
        {
            toast({
                title: "Invalid email",
                description: "Please enter a valid email address",
                status: "error",
                duration: 3000,
                isClosable: true,
            });
            return;
        }

        setIsVerificationStep(true); // Move to the next step immediately

        try
        {
            const response = await fetch(getURL('/auth/send-verification-email'), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, clientID: clientId }),
            });

            const data = await response.json();

            if(response.ok)
            {
                toast({
                    title: "Verification Email Sent",
                    description: "A verification code has been sent to your email.",
                    status: "success",
                    duration: 5000,
                    isClosable: true,
                });
            }
            else
            {
                toast({
                    title: "Error",
                    description: data.message || "An error occurred while sending the verification email",
                    status: "error",
                    duration: 5000,
                    isClosable: true,
                });
            }
        }
        catch (error)
        {
            toast({
                title: "Error",
                description: "An error occurred while sending the verification email",
                status: "error",
                duration: 5000,
                isClosable: true,
            });
        }
    };

    const handleVerificationSubmit = async () =>
    {
        if(!verificationCode)
        {
            toast({
                title: "Verification code is required",
                status: "error",
                duration: 3000,
                isClosable: true,
            });
            return;
        }

        try
        {
            const response = await fetch(getURL('/auth/landing-verify-code'), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, code: verificationCode }),
            });

            const data = await response.json();

            if(response.ok)
            {
                toast({
                    title: "Success",
                    description: "Your email has been verified and registered for alerts.",
                    status: "success",
                    duration: 5000,
                    isClosable: true,
                });
                setIsModalOpen(false);
            }
            else
            {
                toast({
                    title: "Error",
                    description: data.message || "An error occurred during verification",
                    status: "error",
                    duration: 5000,
                    isClosable: true,
                });
            }
        }
        catch (error)
        {
            toast({
                title: "Error",
                description: "An error occurred while verifying your email",
                status: "error",
                duration: 5000,
                isClosable: true,
            });
        }
    };

    const handleKeyPress = (event: React.KeyboardEvent<HTMLInputElement>) =>
    {
        if(event.key === 'Enter')
        {
            if(isVerificationStep)
            {
                handleVerificationSubmit();
            }
            else
            {
                handleEmailSubmit();
            }
        }
    };

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
                    <Flex direction={{ base: 'column', sm: 'row' }} gap={4} mb={4}>
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
                            _hover={{ bg: "whiteAlpha.200" }}
                        >
                            GitHub
                        </Button>
                    </Flex>
                    <Button onClick={handleSubscribeClick} colorScheme="blue" size="sm">
                        Subscribe to updates
                    </Button>
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

            <Modal 
                isOpen={isModalOpen} 
                onClose={() => setIsModalOpen(false)}
                isCentered
                motionPreset="slideInBottom"
                closeOnOverlayClick={false}
            >
                <ModalOverlay bg="blackAlpha.300" backdropFilter="blur(10px)" />
                <ModalContent
                    bg="rgba(20, 25, 43, 0.95)"
                    color="white"
                    borderRadius="xl"
                    boxShadow="xl"
                >
                    <ModalHeader color="orange.400">{isVerificationStep ? "Verify Your Email" : "Subscribe"}</ModalHeader>
                    <ModalCloseButton />
                    <ModalBody>
                        {isVerificationStep ? (
                            <>
                                <Text mb={4}>A verification code has been sent to {email}. It may take a few minutes to arrive, check your spam folder if it doesn't appear in your inbox. Please enter the code below:</Text>
                                <Input
                                    placeholder="Enter verification code"
                                    value={verificationCode}
                                    onChange={(e) => setVerificationCode(e.target.value)}
                                    onKeyPress={handleKeyPress}
                                    bg="whiteAlpha.200"
                                    border="none"
                                    _focus={{ bg: "whiteAlpha.300" }}
                                />
                            </>
                        ) : (
                            <>
                                <Text mb={4}>Enter your email to subscribe:</Text>
                                <Input
                                    placeholder="Enter your email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    onKeyPress={handleKeyPress}
                                    bg="whiteAlpha.200"
                                    border="none"
                                    _focus={{ bg: "whiteAlpha.300" }}
                                />
                            </>
                        )}
                    </ModalBody>
                    <ModalFooter>
                        {isVerificationStep ? (
                            <Button colorScheme="orange" mr={3} onClick={handleVerificationSubmit}>
                                Verify
                            </Button>
                        ) : (
                            <Button colorScheme="orange" mr={3} onClick={handleEmailSubmit}>
                                Submit
                            </Button>
                        )}
                        <Button variant="ghost" onClick={() => setIsModalOpen(false)}>Cancel</Button>
                    </ModalFooter>
                </ModalContent>
            </Modal>
        </Box>
    );
}

export default LandingPage;