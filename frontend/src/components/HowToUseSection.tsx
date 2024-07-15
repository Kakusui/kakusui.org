/*
Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
Use of this source code is governed by an GNU Affero General Public License v3.0
license that can be found in the LICENSE file.
*/

import { Box, Text, Link } from '@chakra-ui/react';

interface HowToUseSectionProps {
    repositoryUrl: string;
    steps: string[];
    notes: string[];
    contactEmail: string;
}

const HowToUseSection: React.FC<HowToUseSectionProps> = ({ repositoryUrl, steps, notes, contactEmail }) => {
    return (
        <Box mt={17} p={4} bg="gray.800" color="gray.500">
            <Text fontSize="lg" mb={4} color="white">How to Use</Text>
            <Text mb={2}>
                For detailed usage instructions, please visit the <Link href={repositoryUrl} color="orange.400" isExternal>GitHub repository README</Link>.
            </Text>
            <Text mb={2}>
                Follow these steps:
            </Text>
            {steps.map((step, index) => (
                <Text key={index}>{index + 1}. {step}<br /></Text>
            ))}
            {notes.map((note, index) => (
                <Text key={index} mt={2}>{note}</Text>
            ))}
            <Text mt={2}>
                If you wish to actually directly use the endpoint, We'd be interested, contact us at <Link href={`mailto:${contactEmail}`} color="orange.400">{contactEmail}</Link>.
            </Text>
        </Box>
    );
};

export default HowToUseSection;