// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// react
import { useEffect, useState, useCallback } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';

// chakra-ui
import { Box, Heading, Text, VStack, List, ListItem, ListIcon, Button, Flex, IconButton, Link, useToast, Spinner } from '@chakra-ui/react';
import { CheckIcon, ArrowBackIcon } from '@chakra-ui/icons';

// images
import landingPageBg from '../assets/images/landing_page.webp';

// utils
import { getURL, getPublishableStripeKey } from '../utils';

// stripe
import { loadStripe } from '@stripe/stripe-js';

// auth context
import { useAuth } from '../contexts/AuthContext';

// lodash
import debounce from 'lodash/debounce';

const stripePromise = loadStripe(getPublishableStripeKey());

function PricingPage()
{
    const toast = useToast();
    const [isProcessing, setIsProcessing] = useState(false);
    const { isLoggedIn, checkLoginStatus, isLoading } = useAuth();
    const navigate = useNavigate();
    const [lastCheckoutAttempt, setLastCheckoutAttempt] = useState(0);

    useEffect(() =>
    {
        document.title = 'Kakusui | Pricing';
        checkLoginStatus();
    }, [checkLoginStatus]);

    const debouncedHandleBuyNow = useCallback(
        debounce(async () =>
        {
            if (!isLoggedIn)
            {
                navigate('/home?openLoginModal=true&redirect=/pricing');
                return;
            }

            setIsProcessing(true);
            try
            {
                const stripe = await stripePromise;
                if (!stripe)
                {
                    throw new Error('Stripe failed to load');
                }

                const response = await fetch(getURL('/stripe/create-checkout-session'), {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                    },
                });

                if (!response.ok)
                {
                    throw new Error('Failed to create checkout session');
                }

                const session = await response.json();

                const result = await stripe.redirectToCheckout({
                    sessionId: session.id
                });

                if (result.error)
                {
                    throw new Error(result.error.message);
                }
            }
            catch (error)
            {
                console.error('Error creating checkout session:', error);
                toast({
                    title: 'Error',
                    description: 'Failed to start checkout process. Please try again.',
                    status: 'error',
                    duration: 5000,
                    isClosable: true,
                });
            }
            finally
            {
                setIsProcessing(false);
            }
        }, 1000),
        [isLoggedIn, navigate, toast]
    );

    const handleBuyNow = () =>
    {
        const now = Date.now();
        if (now - lastCheckoutAttempt < 5000)
        {
            // If less than 5 seconds have passed since the last attempt, show a message
            toast({
                title: 'Please wait',
                description: 'You can only initiate a checkout once every 5 seconds.',
                status: 'warning',
                duration: 3000,
                isClosable: true,
            });
            return;
        }

        setLastCheckoutAttempt(now);
        debouncedHandleBuyNow();
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
                            $5 for 50,000 credits
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
                            <ListItem>
                                <ListIcon as={CheckIcon} color="green.500" />
                                No Captchas
                            </ListItem>
                        </List>
                        
                        <Button
                            onClick={handleBuyNow}
                            colorScheme="orange"
                            size="lg"
                            isLoading={isProcessing || isLoading}
                            loadingText={isProcessing ? "Processing" : "Checking login"}
                            spinner={<Spinner color="white" />}
                            disabled={isProcessing || isLoading}
                        >
                            {isProcessing ? 'Processing' : (isLoading ? 'Checking login' : (isLoggedIn ? 'Buy Now' : 'Login to Purchase'))}
                        </Button>
                        
                        <Text fontSize="sm" textAlign="center">
                            <Link as={RouterLink} to="/pricing/credits" color="orange.300">
                                Click here for a detailed credit cost breakdown by model
                            </Link>
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
