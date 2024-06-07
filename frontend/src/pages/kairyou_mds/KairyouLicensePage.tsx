/*
Copyright Kakusui LLC 2024 (https://kakusui.org) (https://github.com/Kakusui)
Use of this source code is governed by a GNU Lesser General Public License v3.0
license that can be found in the LICENSE file.
*/

import React, { useEffect } from 'react';
import { Box, Heading, Text, Link } from '@chakra-ui/react';

const KairyouLicensePage: React.FC = () => {
    
    useEffect(() => {
        document.title = 'Kakusui - Kairyou | License';

    }, []);

    return (

        
        <Box p={4}>
            <Heading as="h1" mb={4}>License for Kairyou</Heading>

            <Text mb={4}>
                Kairyou is licensed under the GNU Lesser General Public License version 2.1 (LGPLv2.1). This license is designed to allow Kairyou to be used freely in both open-source and proprietary projects while ensuring that modifications to Kairyou itself remain open-source.
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
                The LGPLv2.1 ensures that any modifications to Kairyou must be released under the same LGPLv2.1 license, while allowing you to use Kairyou in your proprietary software.
            </Text>

            <Text mb={4}>
                For a detailed understanding of your rights and obligations under this license, please refer to the full license text.
            </Text>

            <Link href="https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html" color="orange.400" isExternal>
                Read the full LGPLv2.1 License
            </Link>

            <Heading as="h2" size="md" mt={4} mb={2}>License for API and Website</Heading>
            <Text mb={4}>
                The Kairyou instance hosted on <Link href="https://kakusui.org/kairyou" color="orange.400" isExternal>Kakusui.org/kairyou</Link> and its API endpoint at <Link href="https://api.kakusui.org/v1/kairyou" color="orange.400" isExternal>api.kakusui.org/v1/kairyou</Link> are licensed under the GNU General Public License version 3 (GPLv3). This license ensures that the API and website remain free and open-source.
            </Text>

            <Link href="https://www.gnu.org/licenses/gpl-3.0.html" color="orange.400" isExternal>
                Read the full GPLv3 License
            </Link>

            <Text mt={4} fontSize="sm" color="gray.500">
                Last updated: 2024-06-01
            </Text>

            <Box mt={4}>
                <hr />
            </Box>
        </Box>
    );
}

export default KairyouLicensePage;
