/*
Copyright Kakusui LLC 2024 (https://kakusui.org) (https://github.com/Kakusui)
Use of this source code is governed by a GNU General Public License v3.0
license that can be found in the LICENSE file.
*/

import React from 'react';
import { Box, Heading, Text, Link } from '@chakra-ui/react';

const OkisouchiTermsOfServicePage: React.FC = () => {
    return (
        <Box p={4}>
            <Heading as="h1" mb={4}>Terms of Service for Okisouchi (OSC)</Heading>

            <Heading as="h2" size="md" mt={4} mb={2}>1. Introduction</Heading>
            <Text mb={4}>
                Welcome to Okisouchi! By using our software, you agree to be bound by these Terms of Service and all terms incorporated by reference. Please read these terms carefully before using our services.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>2. Eligibility</Heading>
            <Text mb={4}>
                You only need to be old enough to have a Google account to use Okisouchi, in accordance with Google's age requirements.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>3. User Responsibilities</Heading>
            <Heading as="h3" size="sm" mt={2} mb={2}>3a. Software Use and Distribution</Heading>
            <Text mb={4}>
                You are entitled to use, modify, and distribute Okisouchi under the GNU General Public License version 3 (GPLv3). The GPL is a copyleft license that promotes the principles of open-source software. It ensures that any derivative works based on this project must also be distributed under the same GPL license. This license grants you the freedom to use, modify, and distribute the software.
            </Text>
            <Text mb={4}>
                Please note that this information is a brief summary of the GPL. For a detailed understanding of your rights and obligations under this license, please refer to the full license text.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>4. Prohibited Activities</Heading>
            <Text mb={4}>
                You are prohibited from using the software in any way that interferes with its normal operation or with any other user's use and enjoyment of the software.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>5. Modifications to the Software</Heading>
            <Text mb={4}>
                You may modify the source code of Okisouchi for your personal use or to contribute to the community. Since the project is distributed under the GPLv3, any modifications or derivative works must also be distributed under the same license.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>6. Intellectual Property</Heading>
            <Text mb={4}>
                Kakusui possesses no trademarks or other intellectual property rights in the Okisouchi project, other than the rights afforded by the GPLv3. You are free to use the project within the bounds of this license.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>7. Termination</Heading>
            <Text mb={4}>
                Since Okisouchi is an open-source project and users manage their own installations and usage, Kakusui does not terminate your use of the software. You are free to start or cease using the service at your discretion.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>8. Disclaimer of Warranties</Heading>
            <Text mb={4}>
                Okisouchi is provided on an "as is" and "as available" basis without warranties of any kind. Given that Okisouchi is open source, you may choose to improve the code for your own use or for the benefit of the community.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>9. Changes to Terms</Heading>
            <Text mb={4}>
                Kakusui reserves the right to modify or replace these Terms at any time, with or without notice. Changes to these terms will be made as necessary and you are encouraged to review the terms periodically.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>10. Contact Information</Heading>
            <Text mb={4}>
                If you have any questions about these Terms, please contact us at <Link href="mailto:contact@kakusui.org" color="teal.500">contact@kakusui.org</Link>.
            </Text>

            <Text mt={4} fontSize="sm" color="gray.500">
                Last updated: 2024-05-01
            </Text>

            <Box mt={4}>
                <hr />
            </Box>
        </Box>
    );
}

export default OkisouchiTermsOfServicePage;
