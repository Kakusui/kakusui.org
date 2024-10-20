// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// react
import React, { useEffect } from 'react';

// chakra-ui
import { Box, Heading, Text, Link } from '@chakra-ui/react';

const ElucidatePrivacyPolicyPage: React.FC = () => {

    useEffect(() => {
        document.title = 'Kakusui - Elucidate | Privacy Policy';

    }, []);

    return (
        <Box p={4}>
            <Heading as="h1" mb={4}>Privacy Policy for Elucidate</Heading>

            <Heading as="h2" size="md" mt={4} mb={2}>1. Introduction</Heading>
            <Text mb={4}>
                This Privacy Policy outlines how we handle your data when using Elucidate. Your privacy is important to us, and we are committed to protecting your personal information.
                The following applies to Elucidate on our website <Link href="https://kakusui.org/elucidate" color="orange.400">Kakusui.org/elucidate</Link> and its API endpoint at <Link href="https://api.kakusui.org/v1/elucidate" color="orange.400">api.kakusui.org/v1/elucidate</Link>.
                This service is subject to Kakusui's general <Link href="/tos" color="orange.400">Terms of Service</Link> and <Link href="/privacy" color="orange.400">Privacy Policy</Link>. Please review these documents for important information about your rights and responsibilities when using our services.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>2. Data Collection</Heading>
            <Text mb={4}>
                Elucidate itself, the library, collects zero data. However, Elucidate utilizes several third-party APIs that must be considered. By using Elucidate, you agree to the data practices of these third-party services: Google's Gemini, Anthropic's Claude, and OpenAI's GPT. These services have their own privacy policies, and you are advised to review them before using Elucidate.
                These services may change their privacy policies at any time, and Elucidate is not responsible for any changes made by these services. Services may be added or removed from Elucidate at any time.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>3. Data Usage</Heading>
            <Text mb={4}>
                The Elucidate endpoint and its page on our website collect no data nor logs outside of standard endpoint interactions, which contain no info aside from HTTP error codes. Data is limited to what is used for functionality only, and no data is shared ever. We do store some data locally on the user's browser, such as API keys for the services and values from old submissions, but these never leave the user's computer outside of usage requirements.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>4. Data Encryption</Heading>
            <Text mb={4}>
                All data handled by Elucidate on our website and endpoint is encrypted via HTTPS to ensure its security.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>5. Consent</Heading>
            <Text mb={4}>
                By using Elucidate on our website or endpoint, you agree to this privacy policy.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>6. Changes to This Policy</Heading>
            <Text mb={4}>
                Elucidate reserves the right to update this Privacy Policy at any time, with or without notice. Changes will be posted on our website, and you are advised to review this policy periodically for any updates.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>7. Contact Information</Heading>
            <Text mb={4}>
                If you have any questions regarding this Privacy Policy or the data practices of Elucidate, please contact us at <Link href="mailto:contact@kakusui.org" color="orange.400">contact@kakusui.org</Link>.
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

export default ElucidatePrivacyPolicyPage