// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

//react
import React, { useEffect } from 'react';

//chakra-ui
import { Box, Heading, Text, Link, UnorderedList, ListItem } from '@chakra-ui/react';

const TosPage: React.FC = () => {
    useEffect(() => {
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

            <Heading as="h2" size="md" mt={4} mb={2}>2. Description of Service</Heading>
            <Text mb={4}>
                Kakusui provides AI-powered language translation and processing tools, including but not limited to EasyTL, Kairyou, and Elucidate. These services are subject to these Terms of Service.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>3. User Accounts</Heading>
            <Text mb={4}>
                3.1. To access certain features of our services, you must create an account. You can do this by providing an email address and password or by using Google Sign-In.
            </Text>
            <Text mb={4}>
                3.2. If you choose to sign in with Google, you agree to allow us to access basic profile information such as your name and email address. We do not receive or store your Google password.
            </Text>
            <Text mb={4}>
                3.3. You agree to provide accurate, current, and complete information during the registration process and to update such information to keep it accurate, current, and complete.
            </Text>
            <Text mb={4}>
                3.4. You agree that you will not share your account credentials or give others access to your account. You are responsible for all activities that occur under your account.
            </Text>
            <Text mb={4}>
                3.5. We reserve the right to suspend or terminate your account for any reason, including if you breach these terms.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>4. Credits and Payment</Heading>
            <Text mb={4}>
                4.1. Our services operate on a credit system. Credits can be purchased through our platform and are required to use certain features.
            </Text>
            <Text mb={4}>
                4.2. Credit purchases are final and non-refundable. Credits have no cash value and cannot be exchanged for cash.
            </Text>
            <Text mb={4}>
                4.3. We use Stripe for payment processing. By making a purchase, you agree to Stripe's terms of service.
            </Text>
            <Text mb={4}>
                4.4. We reserve the right to change the pricing of credits at any time without prior notice.
            </Text>
            <Text mb={4}>
                4.5. For certain services, you are able to use your own Gemini, Anthropic, and OpenAI API keys.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>5. Use of Service</Heading>
            <Text mb={4}>
                5.1. You agree to use our services only for lawful purposes and in accordance with these Terms of Service.
            </Text>
            <Text mb={4}>
                5.2. You are responsible for all content you submit to our services. You agree not to use our services to transmit any unlawful, infringing, threatening, harassing, defamatory, vulgar, obscene, or otherwise objectionable material.
            </Text>
            <Text mb={4}>
                5.3. We reserve the right to refuse service, terminate accounts, or cancel orders at our sole discretion.
            </Text>
            <Text mb={4}>
                5.4. You are entitled to use the results of our services (including translations, preprocessed text, and other outputs) as you see fit, subject to any applicable laws and regulations.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>6. Intellectual Property</Heading>
            <Text mb={4}>
                6.1. The content, organization, graphics, design, compilation, magnetic translation, digital conversion, and other matters related to our services are protected under applicable copyrights, trademarks, and other proprietary rights.
            </Text>
            <Text mb={4}>
                6.2. The copying, redistribution, use, or publication by you of any such matters or any part of our services, except as allowed by Section 7, is strictly prohibited.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>7. Limited License</Heading>
            <Text mb={4}>
                7.1. We grant you a limited, revocable, and nonexclusive license to access and make personal use of our services.
            </Text>
            <Text mb={4}>
                7.2. This license does not include any resale or commercial use of our services or their contents; any collection and use of any product listings, descriptions, or prices; any derivative use of our services or their contents; any downloading or copying of account information for the benefit of another merchant; or any use of data mining, robots, or similar data gathering and extraction tools.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>8. Disclaimer of Warranties and Limitation of Liability</Heading>
            <Text mb={4}>
                8.1. Our services are provided on an "as is" and "as available" basis. We make no representations or warranties of any kind, express or implied, as to the operation of our services or the information, content, materials, or products included on our services.
            </Text>
            <Text mb={4}>
                8.2. To the full extent permissible by applicable law, we disclaim all warranties, express or implied, including, but not limited to, implied warranties of merchantability and fitness for a particular purpose.
            </Text>
            <Text mb={4}>
                8.3. We will not be liable for any damages of any kind arising from the use of our services, including, but not limited to direct, indirect, incidental, punitive, and consequential damages.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>9. Indemnification</Heading>
            <Text mb={4}>
                You agree to indemnify, defend, and hold harmless Kakusui, its officers, directors, employees, agents, licensors and suppliers from and against all losses, expenses, damages and costs, including reasonable attorneys' fees, resulting from any violation of these Terms of Service or any activity related to your account (including negligent or wrongful conduct) by you or any other person accessing our services using your account.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>10. Third-Party Links</Heading>
            <Text mb={4}>
                Our services may contain links to third-party websites. These links are provided solely as a convenience to you and not as an endorsement by us of the contents on such third-party websites. We are not responsible for the content of linked third-party sites and do not make any representations regarding the content or accuracy of materials on such third-party websites.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>11. Termination</Heading>
            <Text mb={4}>
                We reserve the right, in our sole discretion, to terminate your access to all or part of our services, with or without notice, for any reason, including, without limitation, breach of these Terms of Service.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>12. Changes to Terms</Heading>
            <Text mb={4}>
                We reserve the right to modify these Terms of Service at any time. We will notify users of any significant changes. Your continued use of our services after such modifications constitutes your acceptance of the updated terms.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>13. Governing Law</Heading>
            <Text mb={4}>
                These Terms of Service and your use of our services are governed by and construed in accordance with the laws of the jurisdiction in which Kakusui is registered, without giving effect to any principles of conflicts of law.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>14. Contact Information</Heading>
            <Text mb={4}>
                If you have any questions about these Terms of Service, please contact us at <Link href="mailto:contact@kakusui.org" color="orange.400">contact@kakusui.org</Link>.
            </Text>

            <Text mt={4} fontSize="sm" color="gray.500">
                Last updated: 2024-10-05 <br /> <br />

                Changelog: <br />
                2024-10-05: Various changes to the TOS to reflect new services, account details, credits, and other changes. <br />
            </Text>

            <Box mt={4}>
                <hr />
            </Box>
        </Box>
    );
}

export default TosPage;