// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// react
import React, { useEffect } from 'react';

// chakra-ui
import { Box, Heading, Text, Link } from '@chakra-ui/react';

const EasyTLTermsOfServicePage: React.FC = () => {

    useEffect(() => {
        document.title = 'Kakusui - EasyTL | Terms of Service';

    }, []);

    return (
        <Box p={4}>
            <Heading as="h1" mb={4}>Terms of Service for EasyTL</Heading>

            <Heading as="h2" size="md" mt={4} mb={2}>1. Introduction</Heading>
            <Text mb={4}>
                Welcome to EasyTL! By using our software, you agree to be bound by these Terms of Service and all terms incorporated by reference. Please read these terms carefully before using our services.
                This service is subject to Kakusui's general <Link href="/tos" color="orange.400">Terms of Service</Link> and <Link href="/privacy" color="orange.400">Privacy Policy</Link>. Please review these documents for important information about your rights and responsibilities when using our services.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>2. Eligibility</Heading>
            <Text mb={4}>
                You only need to comply with local jurisdiction laws to use EasyTL.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>3. User Responsibilities</Heading>
            <Heading as="h3" size="sm" mt={2} mb={2}>3a. Software Use and Distribution</Heading>
            <Text mb={4}>
                EasyTL itself, the library, is free and open-source software under the GNU Lesser General Public License version 2.1 (LGPLv2.1). You are entitled to use, modify, and distribute EasyTL under this license. None of Kakusui's terms or licensing applies to the library itself.
            </Text>
            <Text mb={4}>
                However, the EasyTL instance hosted on <Link href="https://kakusui.org/easytl" color="orange.400" isExternal>Kakusui.org/easytl</Link> and its API endpoint at <Link href="https://api.kakusui.org/v1/easytl" color="orange.400" isExternal>api.kakusui.org/v1/easytl</Link> are licensed under the GNU Affero General Public License version 3 (AGPLv3). You are entitled to copy these instances and do whatever with those copies, with no restrictions outside of local jurisdiction laws.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>4. Prohibited Activities</Heading>
            <Text mb={4}>
                You are prohibited from using the website and endpoint in any way that interferes with its normal operation or with any other user's use and enjoyment of the software.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>5. Modifications to the Software</Heading>
            <Text mb={4}>
                You may modify the source code of EasyTL for your personal use or to contribute to the community. Any modifications or derivative works of the library must be distributed under the LGPLv2.1 license, while modifications to the website's instance or endpoint must be distributed under the AGPLv3 license.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>6. Intellectual Property</Heading>
            <Text mb={4}>
                Kakusui does not possess the trademark or any other intellectual property rights on EasyTL, its name, or logo. You are free to use the project within the bounds of the LGPLv2.1 or GPLv3 licenses as applicable.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>7. Termination</Heading>
            <Text mb={4}>
                Since EasyTL itself is open-source and users manage their own installations and usage, Kakusui does not terminate your use of the library. However, the instance of EasyTL on our website or its endpoint could be terminated at any time for any reason, for individuals or everyone everywhere.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>8. Disclaimer of Warranties</Heading>
            <Text mb={4}>
                EasyTL is provided on an "as is" and "as available" basis without warranties of any kind. There is zero warranty, and the endpoint or website could be terminated at any time.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>9. Changes to Terms</Heading>
            <Text mb={4}>
                Kakusui reserves the right to modify or replace these Terms at any time, with or without notice. Changes to these terms will be made as necessary, and you are encouraged to review the terms periodically.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>10. Credit Usage</Heading>
            <Text mb={4}>
                This service uses the Kakusui credit system. Each use of the service will deduct credits from your account based on the current pricing model. Please refer to our pricing page for details.
                You are however free to use the service without any credits if you provide your own API key for Gemini, Anthropic, or OpenAI services.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>11. Data Processing</Heading>
            <Text mb={4}>
                This service utilizes AI models provided by OpenAI, Anthropic, or Google (based on your selection) to process your input. While we do not store your input or the results, please be aware that these third-party AI providers may have access to the data during processing.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>12. Contact Information</Heading>
            <Text mb={4}>
                If you have any questions about these Terms, please contact us at <Link href="mailto:contact@kakusui.org" color="orange.400">contact@kakusui.org</Link>.
            </Text>

            <Text mt={4} fontSize="sm" color="gray.500">
                Last updated: 2024-10-05 <br /> <br />

                Changelog: <br />
                2024-10-05: Various changes to the TOS to reflect new services, account details, credits, and other changes. <br />
                2024-07-15: Switched to AGPLv3 for the API and website. <br />
                2024-06-06: Initial version. <br />
            </Text>

            <Box mt={4}>
                <hr />
            </Box>
        </Box>
    );
}

export default EasyTLTermsOfServicePage;