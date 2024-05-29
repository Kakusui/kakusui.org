/*
Copyright Kakusui LLC 2024 (https://kakusui.org) (https://github.com/Kakusui)
Use of this source code is governed by a GNU General Public License v3.0
license that can be found in the LICENSE file.
*/

import { Box, Button, Heading, Link, Stack, Text } from "@chakra-ui/react";
import { ExternalLinkIcon } from "@chakra-ui/icons";

function OkisouchiPage() {
    return (
        <Box p={4}>
            <Heading as="h1" mb={4}>Okisouchi</Heading>
            <Text mb={4}>
                Okisouchi is a robust, open-source tool for automating the transfer of files from Google Drive
                to designated locations, streamlining file management and organization with user-configured
                settings while ensuring data privacy and adherence to GPLv3 open-source licensing.
            </Text>
            <Link href="https://github.com/Kakusui/osc_interface" isExternal>
                <Button leftIcon={<ExternalLinkIcon />} colorScheme="teal" variant="outline">
                    GitHub
                </Button>
            </Link>

            <Stack direction="row" spacing={4} mt={8}>
                <Link href="/tos" color="teal.500">Terms of Service</Link>
                <Link href="/privacy" color="teal.500">Privacy Policy</Link>
                <Link href="/license" color="teal.500">License</Link>
            </Stack>
        </Box>
    );
}

export default OkisouchiPage;