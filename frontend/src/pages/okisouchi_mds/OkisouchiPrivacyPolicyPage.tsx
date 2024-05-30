/*
Copyright Kakusui LLC 2024 (https://kakusui.org) (https://github.com/Kakusui)
Use of this source code is governed by a GNU General Public License v3.0
license that can be found in the LICENSE file.
*/

import React from 'react';
import { Box, Heading, Text, Link } from '@chakra-ui/react';

const OkisouchiPrivacyPolicyPage: React.FC = () => {
    return (
        <Box p={4}>
            <Heading as="h1" mb={4}>Privacy Policy for Okisouchi (OSC)</Heading>

            <Heading as="h2" size="md" mt={4} mb={2}>1. Introduction</Heading>
            <Text mb={4}>
                This Privacy Policy outlines how we handle your data at Okisouchi. Your privacy is important to us, and we are committed to protecting your personal information.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>2. Data Collection</Heading>
            <Text mb={4}>
                Okisouchi collects the minimum amount of data required to operate effectively. This includes:
                <ul>
                    <li>Information about the files you choose to process.</li>
                    <li>Google Drive account information for file access and management.</li>
                </ul>
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>3. Data Usage</Heading>
            <Text mb={4}>
                Data collected is used exclusively for the functionality of the Okisouchi software. We do not share your data with third parties.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>4. Data Storage</Heading>
            <Text mb={4}>
                All data handled by Okisouchi is stored locally on your device or within your Google Drive account, as per your Google Drive settings.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>5. Data Sharing</Heading>
            <Text mb={4}>
                Okisouchi does not share any data with third parties. All interactions with Google Drive data occur solely through Google's APIs and are bound by the configurations you set in the Okisouchi Interface.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>6. Google API Services User Data Policy</Heading>
            <Text mb={4}>
                We comply with all requirements outlined in Google’s <Link href="https://developers.google.com/terms/api-services-user-data-policy#additional_requirements_for_specific_api_scopes" color="orange.400" isExternal>API Services User Data Policy</Link>, including the Limited Use requirements. This ensures that the use of Google user data is limited to the practices explicitly disclosed in this Privacy Policy.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>7. Consent</Heading>
            <Text mb={4}>
                By connecting your Google Drive account with the Okisouchi Interface and configuring settings within the app, you authorize Okisouchi to manage your files as described above.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>8. Changes to This Policy</Heading>
            <Text mb={4}>
                Okisouchi may update this Privacy Policy at any time. Changes will be posted on our website, and you are advised to review this policy periodically for any updates.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>9. Contact Information</Heading>
            <Text mb={4}>
                If you have any questions regarding this Privacy Policy or the data practices of Okisouchi, please contact us at <Link href="mailto:contact@kakusui.org" color="orange.400">contact@kakusui.org</Link>.
            </Text>

            <Text mt={4} fontSize="sm" color="gray.500">
                Last updated: 2024-05-03
            </Text>

            <Box mt={4}>
                <hr />
            </Box>
        </Box>
    );
}

export default OkisouchiPrivacyPolicyPage;
