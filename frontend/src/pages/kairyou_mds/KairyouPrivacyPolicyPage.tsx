/*
Copyright Kakusui LLC 2024 (https://kakusui.org) (https://github.com/Kakusui)
Use of this source code is governed by a GNU General Public License v3.0
license that can be found in the LICENSE file.
*/

import React from 'react';
import { Box, Heading, Text, Link } from '@chakra-ui/react';

const KairyouPrivacyPolicyPage: React.FC = () => {
    return (
        <Box p={4}>
            <Heading as="h1" mb={4}>Privacy Policy for Kairyou</Heading>

            <Heading as="h2" size="md" mt={4} mb={2}>1. Introduction</Heading>
            <Text mb={4}>
                This Privacy Policy outlines how we handle your data when using Kairyou. Your privacy is important to us, and we are committed to protecting your personal information.
                The following applies to Kairyou on our website <Link href="https://kakusui.org/kairyou" color="orange.400">Kakusui.org/kairyou</Link> and its API endpoint at <Link href="https://api.kakusui.org/v1/kairyou" color="orange.400">api.kakusui.org/v1/kairyou</Link>.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>2. Data Collection</Heading>
            <Text mb={4}>
                Kairyou itself, the library, collects zero data and uses a pre-trained NER model from SpaCy.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>3. Data Usage</Heading>
            <Text mb={4}>
                The Kairyou endpoint and it's page on our website collects no data nor logs outside of standard endpoint interactions, which contain no info aside from HTTP error codes. Data is limited to what is used for functionality only, and no data is shared ever.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>4. Data Encryption</Heading>
            <Text mb={4}>
                All data handled by Kairyou on our website and endpoint is encrypted via HTTPS to ensure its security.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>5. Consent</Heading>
            <Text mb={4}>
                By using Kairyou on our website or endpoint, you agree to this privacy policy.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>6. Changes to This Policy</Heading>
            <Text mb={4}>
                Kairyou reserves the right to update this Privacy Policy at any time, with or without notice. Changes will be posted on our website, and you are advised to review this policy periodically for any updates.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>7. Contact Information</Heading>
            <Text mb={4}>
                If you have any questions regarding this Privacy Policy or the data practices of Kairyou, please contact us at <Link href="mailto:contact@kakusui.org" color="orange.400">contact@kakusui.org</Link>.
            </Text>

            <Text mt={4} fontSize="sm" color="gray.500">
                Last updated: 2024-06-06
            </Text>

            <Text mt={4} fontSize="sm" color="gray.500">
                Changelog: <br />
                2024-06-06: Slight wording changes to clarify the lack of data collection & typo fixes. <br />
                2024-06-01: Initial version.
            </Text>

            <Box mt={4}>
                <hr />
            </Box>
        </Box>
    );
}

export default KairyouPrivacyPolicyPage;
