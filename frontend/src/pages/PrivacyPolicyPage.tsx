// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// react
import React, { useEffect } from 'react';

// chakra-ui
import { Box, Heading, Text, Link, UnorderedList, ListItem } from '@chakra-ui/react';

const PrivacyPolicyPage: React.FC = () =>
{
    useEffect(() =>
    {
        document.title = 'Kakusui | Privacy Policy';
    }, []);

    return (
        <Box p={4}>
            <Heading as="h1" mb={4}>Kakusui Privacy Policy</Heading>

            <Text mb={4}>
                At Kakusui, we are committed to protecting your privacy and ensuring the security of your personal information. This Privacy Policy outlines our practices concerning the collection, use, and protection of your data.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>1. Information We Collect</Heading>
            <Text mb={4}>
                We collect and process only the minimal amount of data necessary to provide our services:
            </Text>
            <UnorderedList mb={4}>
                <ListItem>Email addresses for account creation and verification</ListItem>
                <ListItem>Basic interaction data with our API and website</ListItem>
            </UnorderedList>

            <Heading as="h2" size="md" mt={4} mb={2}>2. How We Use Your Information</Heading>
            <Text mb={4}>
                We use the collected information solely for the purpose of:
            </Text>
            <UnorderedList mb={4}>
                <ListItem>Providing and maintaining our services</ListItem>
                <ListItem>Communicating with you about your account or our services</ListItem>
                <ListItem>Improving our services and user experience</ListItem>
            </UnorderedList>

            <Heading as="h2" size="md" mt={4} mb={2}>3. Data Protection</Heading>
            <Text mb={4}>
                We implement appropriate technical and organizational measures to ensure a level of security appropriate to the risk, including encryption of data in transit and at rest.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>4. No Sale of Personal Data</Heading>
            <Text mb={4}>
                We do not sell, rent, or trade your personal information to third parties under any circumstances. Your data is used exclusively for providing and improving our services.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>5. Data Retention</Heading>
            <Text mb={4}>
                We retain your personal information only for as long as necessary to provide you with our services and as described in this Privacy Policy. We will also retain and use your information to the extent necessary to comply with our legal obligations, resolve disputes, and enforce our policies.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>6. Your Rights</Heading>
            <Text mb={4}>
                You have the right to access, correct, or delete your personal information. If you wish to exercise these rights, please contact us using the information provided below.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>7. Changes to This Privacy Policy</Heading>
            <Text mb={4}>
                We may update our Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy on this page and updating the "Last updated" date.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>8. Contact Us</Heading>
            <Text mb={4}>
                If you have any questions about this Privacy Policy, please contact us at <Link href="mailto:contact@kakusui.org" color="orange.400">contact@kakusui.org</Link>.
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

export default PrivacyPolicyPage;