// Copyright 2024 Kaden Bilyeu (Bikatr7) (https://github.com/Bikatr7) (https://github.com/Bikatr7/kadenbilyeu.com) (https://kadenbilyeu.com)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// react
import { useState, useEffect } from 'react';

// chakra-ui
import { Box, Button, Input, Modal, ModalOverlay, ModalContent, ModalHeader, ModalFooter, ModalBody, ModalCloseButton, Text, useDisclosure, Spinner, Flex } from "@chakra-ui/react";

// util
import { getURL } from '../utils';

// motion
import { motion } from 'framer-motion';

// animations
import { buttonVariants } from '../animations/commonAnimations';

interface LoginProps 
{
    onLogin: () => void;
    onLogout: () => void;
}

const Login: React.FC<LoginProps> = ({ onLogin, onLogout }) => 
{
    const { isOpen, onOpen, onClose } = useDisclosure();
    const [email, setEmail] = useState('');
    const [loginCode, setLoginCode] = useState('');
    const [error, setError] = useState('');
    const [isLoginStep, setIsLoginStep] = useState(false);
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => 
    {
        const checkLoginStatus = async () => 
        {
            setIsLoading(true);
            try 
            {
                const token = localStorage.getItem('token');
                if (token) 
                {
                    const response = await fetch(getURL('/verify-token'), 
                    {
                        method: 'POST',
                        headers: 
                        {
                            'Authorization': `Bearer ${token}`
                        }
                    });

                    if (response.ok) 
                    {
                        const data = await response.json();
                        if (data.valid) 
                        {
                            setIsLoggedIn(true);
                            onLogin();
                        } 
                        else 
                        {
                            throw new Error('Token verification failed');
                        }
                    } 
                    else 
                    {
                        throw new Error('Token verification failed');
                    }
                } 
                else 
                {
                    throw new Error('No token found');
                }
            } 
            catch (error) 
            {
                setIsLoggedIn(false);
                onLogout();
                localStorage.removeItem('token');
            } 
            finally 
            {
                setIsLoading(false);
            }
        };

        checkLoginStatus();
    }, [onLogin, onLogout]);

    const handleClose = () => 
    {
        setEmail('');
        setLoginCode('');
        setError('');
        setIsLoginStep(false);
        onClose();
    };

    const handleEmailSubmit = async () => 
    {
        if (!email || !email.includes('@')) 
        {
            setError('Please enter a valid email address');
            return;
        }

        setIsLoginStep(true); // Move to the next step immediately

        try 
        {
            const response = await fetch(getURL('/send-verification-email'), 
            {
                method: 'POST',
                headers: 
                {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, clientID: 'web-client' })
            });

            if (response.ok) 
            {
                setError(''); // Clear any previous errors
            } 
            else 
            {
                const errorData = await response.json();
                setError(errorData.message || 'Failed to send login code');
            }
        } 
        catch (error) 
        {
            setError('An error occurred. Please try again.');
        }
    };

    const handleLogin = async () => 
    {
        try 
        {
            const response = await fetch(getURL('/login'), 
            {
                method: 'POST',
                headers: 
                {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, verification_code: loginCode })
            });

            if (response.ok) 
            {
                const data = await response.json();
                if (data.access_token) 
                {
                    localStorage.setItem('token', data.access_token);
                    document.cookie = `refresh_token=${data.refresh_token}; path=/; secure; HttpOnly`;
                    setIsLoggedIn(true);
                    onLogin();
                    handleClose();
                } 
                else 
                {
                    setError('Invalid credentials');
                }
            } 
            else
            {
                const errorData = await response.json();
                setError(errorData.message || 'Invalid credentials');
            }
        } 
        catch (error) 
        {
            setError('An error occurred. Please try again.');
        }
    };

    const handleLogout = () => 
    {
        localStorage.removeItem('token');
        setIsLoggedIn(false);
        onLogout();
    };

    const handleKeyPress = (event: React.KeyboardEvent) => 
    {
        if (event.key === 'Enter') 
        {
            if (isLoginStep) 
            {
                handleLogin();
            } 
            else 
            {
                handleEmailSubmit();
            }
        }
    };

    return (
        <>
            <motion.div whileHover="hover" variants={buttonVariants}>
                <Button 
                    onClick={isLoggedIn ? handleLogout : onOpen} 
                    rounded="full"
                    bg="orange.400"
                    color="white"
                    _hover={{ bg: 'orange.500' }}
                    minWidth="70px" 
                    height="40px"    
                >
                    {isLoading ? <Spinner size="sm" /> : (isLoggedIn ? 'Logout' : 'Login')}
                </Button>
            </motion.div>
            <Modal isOpen={isOpen} onClose={handleClose} isCentered motionPreset="slideInBottom">
                <ModalOverlay bg="blackAlpha.300" backdropFilter="blur(10px)" />
                <ModalContent
                    bg="rgba(20, 25, 43, 0.95)"
                    color="white"
                    borderRadius="xl"
                    boxShadow="xl"
                >
                    <ModalHeader color="orange.400">{isLoginStep ? "Check Your Email" : "Login"}</ModalHeader>
                    <ModalCloseButton />
                    <ModalBody>
                        <Flex direction="column" gap={4}>
                            {isLoginStep ? (
                                <>
                                    <Text>A login code has been sent to {email}. Please enter the code below:</Text>
                                    <Input
                                        placeholder="Enter login code"
                                        value={loginCode}
                                        onChange={(e) => setLoginCode(e.target.value)}
                                        onKeyPress={handleKeyPress}
                                        bg="whiteAlpha.200"
                                        border="none"
                                        _focus={{ bg: "whiteAlpha.300" }}
                                    />
                                </>
                            ) : (
                                <>
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
                            {error && (
                                <Text color="red.500" mt={2}>
                                    {error}
                                </Text>
                            )}
                        </Flex>
                    </ModalBody>
                    <ModalFooter>
                        <Flex width="100%" justify="space-between">
                            {isLoginStep && (
                                <Button variant="ghost" onClick={() => setIsLoginStep(false)} _hover={{ bg: "whiteAlpha.200" }}>
                                    Back
                                </Button>
                            )}
                            <Box>
                                <Button variant="ghost" mr={3} onClick={handleClose} _hover={{ bg: "whiteAlpha.200" }}>
                                    Cancel
                                </Button>
                                {isLoginStep ? (
                                    <Button colorScheme="orange" onClick={handleLogin}>
                                        Login
                                    </Button>
                                ) : (
                                    <Button colorScheme="orange" onClick={handleEmailSubmit}>
                                        Send Code
                                    </Button>
                                )}
                            </Box>
                        </Flex>
                    </ModalFooter>
                </ModalContent>
            </Modal>
        </>
    );
};

export default Login;