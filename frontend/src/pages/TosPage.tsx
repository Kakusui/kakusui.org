// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// react
import React, { useEffect } from 'react';

// chakra-ui
import { Box, Heading, Text, Link, UnorderedList, ListItem } from '@chakra-ui/react';

const TosPage: React.FC = () =>
{
    useEffect(() =>
    {
        document.title = 'Kakusui | Terms of Service';
    }, []);

    return (
        <Box p={4}>
            <Heading as="h1" mb={4}>Kakusui Terms of Service</Heading>

            <Text mb={4}>
                Welcome to Kakusui. By using our services, you agree to be bound by these Terms of Service. Please read them carefully.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>1. Acceptance of Terms</Heading>
            <Text mb={4}>
                By accessing or using Kakusui's services, you agree to comply with and be bound by these Terms of Service. If you do not agree to these terms, please do not use our services.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>2. Product-Specific Terms</Heading>
            <Text mb={4}>
                In addition to these general terms, please review the specific Terms of Service for our products:
            </Text>
            <UnorderedList mb={4}>
                <ListItem>
                    <Link href="/kairyou/tos" color="orange.400">Kairyou Terms of Service</Link>
                </ListItem>
                <ListItem>
                    <Link href="/easytl/tos" color="orange.400">EasyTL Terms of Service</Link>
                </ListItem>
                <ListItem>
                    <Link href="/elucidate/tos" color="orange.400">Elucidate Terms of Service</Link>
                </ListItem>
            </UnorderedList>

            <Heading as="h2" size="md" mt={4} mb={2}>3. Account Creation and Use</Heading>
            <Text mb={4}>
                3.1. You may create an account to access certain features of our services. When creating an account, you must provide accurate and complete information. You are required to verify your email address to make an account.
            </Text>
            <Text mb={4}>
                3.2. You are responsible for maintaining the confidentiality of your account and email address and for restricting access to your account.
            </Text>
            <Text mb={4}>
                3.3. You agree to accept responsibility for all activities that occur under your account.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>4. Service Fees</Heading>
            <Text mb={4}>
                4.1. Currently, our services are provided free of charge. There are no fees associated with creating an account or using our services.
            </Text>
            <Text mb={4}>
                4.2. We reserve the right to introduce fees for certain services in the future. Any such changes will be communicated to you in advance. 
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>5. Termination of Service</Heading>
            <Text mb={4}>
                5.1. We reserve the right to terminate or suspend your access to Kakusui and its services, in whole or in part, at any time and for any reason without prior notice or liability.
            </Text>
            <Text mb={4}>
                5.2. We may remove or disable your account, content, or access to our services if we believe that you have violated these Terms of Service or that your conduct may harm Kakusui or others.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>6. Changes to Terms</Heading>
            <Text mb={4}>
                We reserve the right to modify these Terms of Service at any time. We will notify users of any significant changes. Your continued use of our services after such modifications constitutes your acceptance of the updated terms.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>7. Contact Information</Heading>
            <Text mb={4}>
                If you have any questions about these Terms of Service, please contact us at <Link href="mailto:contact@kakusui.org" color="orange.400">contact@kakusui.org</Link>.
            </Text>

            <Text mt={4} fontSize="sm" color="gray.500">
                Last updated: 2024-09-21
            </Text>

            <Box mt={4}>
                <hr />
            </Box>
        </Box>
    );
}

export default TosPage;
