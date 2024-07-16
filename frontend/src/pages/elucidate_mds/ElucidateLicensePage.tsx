/*
Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
Use of this source code is governed by an GNU Affero General Public License v3.0
license that can be found in the LICENSE file.
*/

import React, { useEffect } from 'react';
import { Box, Heading, Text, Link } from '@chakra-ui/react';

const ElucidateLicensePage: React.FC = () => {

    useEffect(() => {
        document.title = 'Kakusui - Elucidate | License';

    }, []);

    return (
        <Box p={4}>
            <Heading as="h1" mb={4}>License for Elucidate</Heading>

            <Text mb={4}>
                Elucidate is licensed under the GNU Lesser General Public License version 2.1 (LGPLv2.1). This license is designed to allow Elucidate to be used freely in both open-source and proprietary projects while ensuring that modifications to Elucidate itself remain open-source.
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>Key Points of LGPLv2.1</Heading>
            <Text mb={4}>
                <ul>
                    <li><strong>Freedom to Use:</strong> You are free to use the library in your applications, both open-source and proprietary.</li>
                    <li><strong>Freedom to Study and Modify:</strong> You can study how the library works and change it to suit your needs.</li>
                    <li><strong>Freedom to Distribute:</strong> You can distribute copies of the library.</li>
                    <li><strong>Freedom to Distribute Modified Versions:</strong> You can distribute your modifications to the library, under the same LGPLv2.1 license.</li>
                </ul>
            </Text>

            <Text mb={4}>
                The LGPLv2.1 ensures that any modifications to Elucidate must be released under the same LGPLv2.1 license, while allowing you to use Elucidate in your proprietary software.
            </Text>

            <Text mb={4}>
                For a detailed understanding of your rights and obligations under this license, please refer to the full license text.
            </Text>

            <Link href="https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html" color="orange.400" isExternal>
                Read the full LGPLv2.1 License
            </Link>

            <Heading as="h2" size="md" mt={4} mb={2}>License for API and Website</Heading>
            <Text mb={4}>
                The Elucidate instance hosted on <Link href="https://kakusui.org/elucidate" color="orange.400" isExternal>Kakusui.org/elucidate</Link> and its API endpoint at <Link href="https://api.kakusui.org/v1/elucidate" color="orange.400" isExternal>api.kakusui.org/v1/elucidate</Link> are licensed under the GNU Affero General Public License version 3 (AGPLv3). This license ensures that the API and website remain free and open-source.
            </Text>

            <Link href="https://www.gnu.org/licenses/agpl-3.0.html" color="orange.400" isExternal>
                Read the full APGLv3 License
            </Link>

            <Text mt={4} fontSize="sm" color="gray.500">
                Last updated: 2024-07-15
            </Text>

            <Box mt={4}>
                <hr />
            </Box>
        </Box>
    );
}

export default ElucidateLicensePage;