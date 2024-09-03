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

// jwt-decode
import { jwtDecode } from 'jwt-decode';

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
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [totp, setTotp] = useState('');
    const [error, setError] = useState('');
    const [step, setStep] = useState(1);
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [isLoading, setIsLoading] = useState(true);

    const isTokenExpired = (token: string) => 
    {
        try 
        {
            const decoded = jwtDecode(token);
            const currentTime = Date.now() / 1000;
            return decoded.exp ? decoded.exp < currentTime : true;
        } 
        catch (error) 
        {
            return true;
        }
    };

    useEffect(() => 
    {
        const checkLoginStatus = async () => 
        {
            setIsLoading(true);
            try 
            {
                const token = localStorage.getItem('token');
                if (token && !isTokenExpired(token)) 
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
                    throw new Error('No token or expired token');
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

    const handleNext = () => 
    {
        setStep(2);
    };

    const handleBack = () => 
    {
        setStep(1);
    };

    const handleClose = () => 
    {
        setUsername('');
        setPassword('');
        setTotp('');
        setError('');
        setStep(1);
        onClose();
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
                body: JSON.stringify({ username, password, totp })
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
                    setError('Invalid credentials or TOTP code');
                }
            } 
            else
            {
                const errorData = await response.json();
                setError(`Error: ${errorData.detail || 'Invalid credentials or TOTP code'}`);
            }
        } 
        catch (error) 
        {
            setError('An error occurred. Please try again.');
        }
    };

    const handleKeyPress = (event: React.KeyboardEvent) => 
    {
        if (event.key === 'Enter') 
        {
            if (step === 1) 
            {
                handleNext();
            } 
            else 
            {
                handleLogin();
            }
        }
    };

    const handleLogout = () => 
    {
        localStorage.removeItem('token');
        setIsLoggedIn(false);
        onLogout();
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
                    <ModalHeader color="orange.400">Login</ModalHeader>
                    <ModalCloseButton color="orange.400" />
                    <ModalBody>
                        <Flex direction="column" gap={4}>
                            {step === 1 ? (
                                <>
                                    <Input
                                        placeholder="Username"
                                        value={username}
                                        onChange={(e) => setUsername(e.target.value)}
                                        onKeyPress={handleKeyPress}
                                        autoComplete="username"
                                        bg="whiteAlpha.200"
                                        border="none"
                                        _focus={{ bg: "whiteAlpha.300" }}
                                    />
                                    <Input
                                        placeholder="Password"
                                        type="password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        onKeyPress={handleKeyPress}
                                        autoComplete="current-password"
                                        bg="whiteAlpha.200"
                                        border="none"
                                        _focus={{ bg: "whiteAlpha.300" }}
                                    />
                                </>
                            ) : (
                                <>
                                    <Text color="orange.400">Enter your TOTP code</Text>
                                    <Input
                                        placeholder="Enter 6-digit code"
                                        value={totp}
                                        onChange={(e) => setTotp(e.target.value)}
                                        onKeyPress={handleKeyPress}
                                        autoComplete="off"
                                        inputMode="numeric"
                                        pattern="\d{6}"
                                        maxLength={6}
                                        name="totp"
                                        aria-label="Time-based One-time Password"
                                        type="text"
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
                            {step === 2 && (
                                <Button variant="ghost" onClick={handleBack} _hover={{ bg: "whiteAlpha.200" }}>
                                    Back
                                </Button>
                            )}
                            <Box>
                                <Button variant="ghost" mr={3} onClick={handleClose} _hover={{ bg: "whiteAlpha.200" }}>
                                    Cancel
                                </Button>
                                {step === 1 ? (
                                    <Button colorScheme="orange" onClick={handleNext}>
                                        Next
                                    </Button>
                                ) : (
                                    <Button colorScheme="orange" onClick={handleLogin}>
                                        Verify TOTP
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