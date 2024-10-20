// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// react
import { useEffect, useState } from 'react';
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

const stripePromise = loadStripe(getPublishableStripeKey());

function PricingPage()
{
    const toast = useToast();
    const [isLoading, setIsLoading] = useState(false);
    const { isLoggedIn, checkLoginStatus } = useAuth();
    const navigate = useNavigate();

    useEffect(() =>
    {
        document.title = 'Kakusui | Pricing';
        checkLoginStatus();
    }, [checkLoginStatus]);

    const handleBuyNow = async () =>
    {
        if (!isLoggedIn)
        {
            // Redirect to home page with a query parameter to open the login modal
            navigate('/home?openLoginModal=true');
            return;
        }

        setIsLoading(true);
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
            setIsLoading(false);
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
                            isLoading={isLoading}
                            loadingText="Processing"
                            spinner={<Spinner color="white" />}
                            disabled={isLoading}
                        >
                            {isLoading ? 'Processing' : (isLoggedIn ? 'Buy Now' : 'Login to Purchase')}
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
