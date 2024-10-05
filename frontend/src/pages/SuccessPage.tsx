// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

import { useEffect, useState, useCallback } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Box, Heading, Text, VStack, Button, Spinner, Center } from '@chakra-ui/react';
import { getURL } from '../utils';
import { useAuth } from '../contexts/AuthContext';

function SuccessPage()
{
    const [verificationStatus, setVerificationStatus] = useState('verifying');
    const [isVerified, setIsVerified] = useState(false);
    const location = useLocation();
    const navigate = useNavigate();
    const { isLoggedIn, checkLoginStatus } = useAuth();

    const verifyPayment = useCallback(async () =>
    {
        if(isVerified)
        {
            return;
        }

        const params = new URLSearchParams(location.search);
        const sessionId = params.get('session_id');

        if(!sessionId)
        {
            setVerificationStatus('error');
            return;
        }

        if(!isLoggedIn)
        {
            await checkLoginStatus();
        }

        try
        {
            const accessToken = localStorage.getItem('access_token');
            if(!accessToken)
            {
                throw new Error('No access token found');
            }

            const response = await fetch(getURL('/stripe/verify-payment'), 
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`
                },
                body: JSON.stringify({ session_id: sessionId })
            });

            const data = await response.json();

            if(response.ok && data.success)
            {
                setVerificationStatus('success');
                setIsVerified(true);
                await checkLoginStatus(true); // Refresh user info including credits
            }
            else
            {
                setVerificationStatus('error');
            }
        }
        catch (error)
        {
            console.error('Error verifying payment:', error);
            setVerificationStatus('error');
        }
    }, [location, isLoggedIn, checkLoginStatus, isVerified]);

    useEffect(() =>
    {
        if(!isVerified)
        {
            verifyPayment();
        }
    }, [verifyPayment, isVerified]);

    return (
        <Center minHeight="100vh">
            <VStack spacing={6} align="stretch" maxWidth="600px" width="90%" p={8}>
                <Heading as="h1" size="xl" textAlign="center" color="orange.400">
                    Payment Verification
                </Heading>

                {verificationStatus === 'verifying' && (
                    <Box textAlign="center">
                        <Spinner size="xl" color="orange.500" mb={4} />
                        <Text>Verifying your payment...</Text>
                    </Box>
                )}

                {verificationStatus === 'success' && (
                    <>
                        <Text fontSize="xl" color="green.500" textAlign="center">
                            Payment successful! Credits have been added to your account.
                        </Text>
                        <Button colorScheme="orange" onClick={() => navigate('/home')}>
                            Go to Home
                        </Button>
                    </>
                )}

                {verificationStatus === 'error' && (
                    <>
                        <Text fontSize="xl" color="red.500" textAlign="center">
                            There was an error verifying your payment. Please contact support at support@kakusui.org.
                        </Text>
                        <Button colorScheme="orange" onClick={() => navigate('/home')}>
                            Go to Home
                        </Button>
                    </>
                )}
            </VStack>
        </Center>
    );
}

export default SuccessPage;