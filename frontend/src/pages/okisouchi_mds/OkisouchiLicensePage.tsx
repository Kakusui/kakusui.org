/*
Copyright Kakusui LLC 2024 (https://kakusui.org) (https://github.com/Kakusui)
Use of this source code is governed by a GNU General Public License v3.0
license that can be found in the LICENSE file.
*/

import React from 'react';
import { Box, Heading, Text, Link } from '@chakra-ui/react';

const OkisouchiLicensePage: React.FC = () => {
    return (
        <Box p={4}>
            <Heading as="h1" mb={4}>License for Okisouchi (OSC)</Heading>

            <Text mb={4}>
                Okisouchi is licensed under the GNU General Public License version 3 (GPLv3). This license is designed to ensure that Okisouchi remains free and open-source, providing the following freedoms:
            </Text>

            <Heading as="h2" size="md" mt={4} mb={2}>Key Points of GPLv3</Heading>
            <Text mb={4}>
                <ul>
                    <li><strong>Freedom to Use:</strong> You are free to use the software for any purpose.</li>
                    <li><strong>Freedom to Study and Modify:</strong> You can study how the program works and change it to make it do what you wish.</li>
                    <li><strong>Freedom to Distribute:</strong> You can redistribute copies of the original program so you can help others.</li>
                    <li><strong>Freedom to Distribute Modified Versions:</strong> You can distribute copies of your modified versions to others.</li>
                </ul>
            </Text>

            <Text mb={4}>
                The GPLv3 ensures that any derivative works you create based on Okisouchi must also be licensed under the GPLv3, promoting the principles of open-source software and collaboration.
            </Text>

            <Text mb={4}>
                For a detailed understanding of your rights and obligations under this license, please refer to the full license text.
            </Text>

            <Link href="https://www.gnu.org/licenses/gpl-3.0.html" color="teal.500" isExternal>
                Read the full GPLv3 License
            </Link>

            <Text mt={4} fontSize="sm" color="gray.500">
                Last updated: 2024-05-01
            </Text>

            <Box mt={4}>
                <hr />
            </Box>
        </Box>
    );
}

export default OkisouchiLicensePage;
