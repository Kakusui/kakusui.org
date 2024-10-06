// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

//react
import React, { useEffect } from 'react';

//chakra-ui
import { Box, Heading, Text, Link, UnorderedList, ListItem } from '@chakra-ui/react';

const PrivacyPolicyPage: React.FC = () => {
    useEffect(() => {
        document.title = 'Kakusui | Privacy Policy';
    }, []);

    return (
        <Box p={4}>
            <Heading as="h1" mb={4}>Kakusui Privacy Policy</Heading>

            <Text mb={4}>
                At Kakusui, we are committed to protecting your privacy and ensuring the security of your personal information. This Privacy Policy outlines our practices concerning the collection, use, and protection of your data.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>Introduction</Heading>
            <Text mb={4}>
                Welcome to Kakusui, by using our services, you agree to be bound by this Privacy Policy. Please do not use our services if you do not agree to this policy.
            </Text>

            <Text mb={4}>
                In addition to these general terms, please review the specific Privacy Policy for our products:
            </Text>
            <UnorderedList mb={4}>
                <ListItem>
                    <Link href="/kairyou/privacy" color="orange.400">Kairyou Privacy Policy</Link>
                </ListItem>
                <ListItem>
                    <Link href="/easytl/privacy" color="orange.400">EasyTL Privacy Policy</Link>
                </ListItem>
                <ListItem>
                    <Link href="/elucidate/privacy" color="orange.400">Elucidate Privacy Policy</Link>
                </ListItem>
            </UnorderedList>

            <Heading as="h2" size="md" mt={4} mb={2}>1. Information We Collect</Heading>
            <Text mb={4}>
                We collect and process the following types of information:
            </Text>
            <UnorderedList mb={4}>
                <ListItem>Email addresses for account creation and verification</ListItem>
                <ListItem>Google account information if you choose to sign in with Google</ListItem>
                <ListItem>Payment information (processed securely through Stripe)</ListItem>
                <ListItem>Usage data related to our services</ListItem>
                <ListItem>Information you provide when using our translation and text processing tools</ListItem>
            </UnorderedList>

            <Heading as="h2" size="md" mt={4} mb={2}>2. How We Use Your Information</Heading>
            <Text mb={4}>
                We use the collected information for the following purposes:
            </Text>
            <UnorderedList mb={4}>
                <ListItem>Providing and maintaining our services</ListItem>
                <ListItem>Processing payments and managing your account balance</ListItem>
                <ListItem>Communicating with you about your account or our services</ListItem>
                <ListItem>Improving our services and user experience</ListItem>
                <ListItem>Complying with legal obligations</ListItem>
            </UnorderedList>

            <Heading as="h2" size="md" mt={4} mb={2}>3. Data Protection</Heading>
            <Text mb={4}>
                We implement appropriate technical and organizational measures to ensure a level of security appropriate to the risk, including encryption of data in transit and at rest.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>4. Third-Party Services</Heading>
            <Text mb={4}>
                We use third-party services for certain aspects of our operations:
            </Text>
            <UnorderedList mb={4}>
                <ListItem>Google for authentication (if you choose to sign in with Google)</ListItem>
                <ListItem>Stripe for payment processing</ListItem>
                <ListItem>OpenAI, Anthropic, and Google for AI-powered language processing</ListItem>
            </UnorderedList>
            <Text mb={4}>
                These services have their own privacy policies, and we encourage you to review them. When you sign in with Google, we receive basic profile information such as your name and email address. We do not receive or store your Google password.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>5. Data Retention</Heading>
            <Text mb={4}>
                We retain your personal information only for as long as necessary to provide you with our services and as described in this Privacy Policy. We will also retain and use your information to the extent necessary to comply with our legal obligations, resolve disputes, and enforce our policies.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>6. Your Rights</Heading>
            <Text mb={4}>
                Depending on your location, you may have certain rights regarding your personal data, including:
            </Text>
            <UnorderedList mb={4}>
                <ListItem>The right to access and receive a copy of your personal data</ListItem>
                <ListItem>The right to rectify or update your personal data</ListItem>
                <ListItem>The right to erase your personal data</ListItem>
                <ListItem>The right to restrict processing of your personal data</ListItem>
                <ListItem>The right to object to processing of your personal data</ListItem>
                <ListItem>The right to data portability</ListItem>
            </UnorderedList>
            <Text mb={4}>
                To exercise these rights, please contact us using the information provided in the "Contact Us" section.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>7. Cookies and Tracking</Heading>
            <Text mb={4}>
                We use cookies and similar tracking technologies to track activity on our service and hold certain information. You can instruct your browser to refuse all cookies or to indicate when a cookie is being sent.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>8. Children's Privacy</Heading>
            <Text mb={4}>
                Our service is not intended for use by children under the age of 13. We do not knowingly collect personal information from children under 13. If we become aware that we have collected personal data from a child under 13 without verification of parental consent, we take steps to remove that information from our servers.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>9. Changes to This Privacy Policy</Heading>
            <Text mb={4}>
                We may update our Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy on this page and updating the "Last updated" date.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>10. Notes</Heading>
            <Text mb={4}></Text>
                While we do collect some information, we do not use it to track you or your activities. Nor will it ever be sold to third parties. The bare minimum information we collect is used for the sole purpose of providing and improving our services.
            <Text mb={4}></Text>

            <Heading as="h2" size="md" mt={4} mb={2}>11. Contact Us</Heading>
            <Text mb={4}>
                If you have any questions about this Privacy Policy, please contact us at <Link href="mailto:contact@kakusui.org" color="orange.400">contact@kakusui.org</Link>.
            </Text>

            <Text mt={4} fontSize="sm" color="gray.500">
                Last updated: 2024-10-05 <br /> <br />

                Changelog: <br />
                2024-10-05: Various changes to the Privacy Policy to reflect new services, account details, credits, and other changes. <br />
            </Text>

            <Box mt={4}>
                <hr />
            </Box>
        </Box>
    );
}

export default PrivacyPolicyPage;