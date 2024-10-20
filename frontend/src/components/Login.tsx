// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// react
import { useState, useEffect } from 'react';

// chakra-ui
import { Box, Button, Input, Modal, ModalOverlay, ModalContent, ModalHeader, ModalFooter, ModalBody, ModalCloseButton, Text, useDisclosure, Spinner, Flex, useToast, Divider, Center } from "@chakra-ui/react";

// util
import { getURL } from '../utils';

// motion
import { motion } from 'framer-motion';

// animations
import { buttonVariants } from '../animations/commonAnimations';

// auth
import { useAuth } from '../contexts/AuthContext';

// google oauth
import { GoogleLogin } from '@react-oauth/google';

interface LoginProps {
    isOpen?: boolean;
    onClose?: () => void;
    onLoginClick?: () => void;
    hidden?: boolean;
}

const Login: React.FC<LoginProps> = ({ isOpen: propIsOpen, onClose: propOnClose, onLoginClick, hidden = false }) => 
{
    const { isOpen: internalIsOpen, onOpen: internalOnOpen, onClose: internalOnClose } = useDisclosure();
    const [email, setEmail] = useState('');
    const [loginCode, setLoginCode] = useState('');
    const [isLoginStep, setIsLoginStep] = useState(false);
    const [isSignUp, setIsSignUp] = useState(false);
    const [clientId, setClientId] = useState('');
    const toast = useToast();
    const { isLoggedIn, login, logout, isLoading } = useAuth();

    const isControlled = propIsOpen !== undefined;
    const isOpen = isControlled ? propIsOpen : internalIsOpen;
    const onClose = isControlled ? propOnClose : internalOnClose;

    useEffect(() =>
    {
        let storedClientId = localStorage.getItem('kakusui_client_id');
        if (!storedClientId)
        {
            storedClientId = generateClientId();
            localStorage.setItem('kakusui_client_id', storedClientId);
        }
        setClientId(storedClientId);
    }, []);

    const generateClientId = () =>
    {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) 
        {
            var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    };

    const handleClose = () => 
    {
        setEmail('');
        setLoginCode('');
        setIsLoginStep(false);
        if (onClose) onClose();
    };

    const showToast = (title: string, description: string, status: "error" | "info" | "warning" | "success") => 
    {
        toast({
            title,
            description,
            status,
            duration: 5000,
            isClosable: true,
        });
    };

    const handleEmailSubmit = async () => 
    {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if(!email || !emailRegex.test(email)) 
        {
            showToast("Invalid Email", "Please enter a valid email address", "error");
            return;
        }

        try 
        {
            const checkUserResponse = await fetch(getURL('/auth/check-email-registration'), 
            {
                method: 'POST',
                headers: 
                {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, clientID: clientId }),
                credentials: 'include'
            });

            if(checkUserResponse.ok) 
            {
                const userData = await checkUserResponse.json();
                if(!userData.registered && !isSignUp)
                {
                    showToast("Not Registered", "This email is not registered. Please sign up first.", "error");
                    setIsLoginStep(false);
                    return;
                }
                if(userData.registered && isSignUp)
                {
                    setIsLoginStep(false);
                    showToast("Already Registered", "This email is already registered. Please log in instead.", "error");
                    return;
                }

                setIsLoginStep(true);

                const response = await fetch(getURL('/auth/send-verification-email'), 
                {
                    method: 'POST',
                    headers: 
                    {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ email, clientID: clientId }),
                    credentials: 'include'
                });

                if(!response.ok) 
                {
                    const errorData = await response.json();
                    showToast("Error", errorData.message || 'Failed to send login code', "error");
                    setIsLoginStep(false);
                }
            } 
            else 
            {
                showToast("Error", "Failed to check user registration", "error");
                setIsLoginStep(false);
            }
        } 
        catch (error) 
        {
            showToast("Error", "An error occurred. Please try again.", "error");
            setIsLoginStep(false);
        }
    };

    const handleSubmit = async () => 
    {
        try 
        {
            const endpoint = isSignUp ? '/auth/signup' : '/auth/login';
            const response = await fetch(getURL(endpoint), 
            {
                method: 'POST',
                headers: 
                {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, verification_code: loginCode }),
                credentials: 'include'
            });

            if (response.ok) 
            {
                const data = await response.json();
                if (data.access_token) 
                {
                    await login(data.access_token);
                    showToast("Success", `Successfully ${isSignUp ? "signed up" : "logged in"}`, "success");
                    if (onClose) onClose();
                } 
                else 
                {
                    showToast("Error", "Invalid credentials", "error");
                }
            } 
            else
            {
                const errorData = await response.json();
                showToast("Error", errorData.message || 'Invalid credentials', "error");
            }
        } 
        catch (error) 
        {
            showToast("Error", "An error occurred. Please try again.", "error");
        }
    };

    const toggleSignUp = () => 
    {
        setIsSignUp(!isSignUp);
        setIsLoginStep(false);
        setEmail('');
        setLoginCode('');
    };

    const handleKeyPress = (event: React.KeyboardEvent) => 
    {
        if (event.key === 'Enter') 
        {
            if (isLoginStep) 
            {
                handleSubmit();
            } 
            else 
            {
                handleEmailSubmit();
            }
        }
    };

    const handleGoogleLogin = async (credentialResponse: any) =>
    {
        try
        {
            const response = await fetch(getURL('/auth/google-login'), 
            {
                method: 'POST',
                headers: 
                {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ token: credentialResponse.credential }),
                credentials: 'include'
            });

            if (response.ok)
            {
                const data = await response.json();
                if (data.access_token)
                {
                    await login(data.access_token);
                    showToast("Success", "Successfully logged in with Google", "success");
                    if (onClose) onClose();
                }
                else
                {
                    showToast("Error", "Failed to log in with Google", "error");
                }
            }
            else
            {
                const errorData = await response.json();
                showToast("Error", errorData.message || 'Failed to log in with Google', "error");
            }
        }
        catch (error)
        {
            showToast("Error", "An error occurred during Google login. Please try again.", "error");
        }
    };

    const handleButtonClick = () => 
    {
        if (isLoggedIn) 
        {
            logout();
            showToast("Success", "Successfully logged out", "success");
        } 
        else 
        {
            if (onLoginClick) 
            {
                onLoginClick();
            } 
            else 
            {
                internalOnOpen();
            }
        }
    };

    return (
        <>
            {!hidden && (
                <motion.div whileHover="hover" variants={buttonVariants}>
                    <Button 
                        onClick={handleButtonClick}
                        rounded="full"
                        bg="orange.400"
                        color="white"
                        _hover={{ bg: 'orange.500' }}
                        minWidth="70px" 
                        height="40px"    
                        disabled={isLoading}
                    >
                        {isLoading ? (
                            <Spinner size="sm" color="white" />
                        ) : (
                            isLoggedIn ? 'Logout' : 'Login'
                        )}
                    </Button>
                </motion.div>
            )}
            <Modal 
                isOpen={isOpen} 
                onClose={handleClose} 
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
                    <ModalHeader color="orange.400">{isSignUp ? "Sign Up" : "Login"}</ModalHeader>
                    <ModalCloseButton />
                    <ModalBody>
                        <Flex direction="column" gap={4}>
                            {isLoginStep ? (
                                <>
                                    <Text>A {isSignUp ? "signup" : "login"} code has been sent to {email}. Please enter the code below:</Text>
                                    <Input
                                        placeholder="Enter code"
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
                            <Divider my={4} />
                            <Text textAlign="center">Or</Text>
                            <Center>
                                <GoogleLogin
                                    onSuccess={handleGoogleLogin}
                                    onError={() => showToast("Error", "Google login failed", "error")}
                                />
                            </Center>
                        </Flex>
                    </ModalBody>
                    <ModalFooter>
                        <Flex width="100%" justify="space-between" direction="column" align="center">
                            <Flex width="100%" justify="space-between" mb={4}>
                                <Box>
                                    <Button variant="ghost" mr={3} onClick={handleClose} _hover={{ bg: "whiteAlpha.200" }}>
                                        Close
                                    </Button>
                                    {isLoginStep && (
                                        <Button variant="ghost" onClick={() => setIsLoginStep(false)} _hover={{ bg: "whiteAlpha.200" }}>
                                            Back
                                        </Button>
                                    )}
                                </Box>
                                <Box>
                                    {isLoginStep ? (
                                        <Button colorScheme="orange" onClick={handleSubmit}>
                                            {isSignUp ? "Sign Up" : "Login"}
                                        </Button>
                                    ) : (
                                        <Button colorScheme="orange" onClick={handleEmailSubmit}>
                                            Send Code
                                        </Button>
                                    )}
                                </Box>
                            </Flex>
                            {!isLoginStep && (
                                <Button variant="link" color="orange.400" onClick={toggleSignUp}>
                                    {isSignUp ? "Already have an account? Login" : "Don't have an account? Sign Up"}
                                </Button>
                            )}
                        </Flex>
                    </ModalFooter>
                </ModalContent>
            </Modal>
        </>
    );
};

export default Login;
