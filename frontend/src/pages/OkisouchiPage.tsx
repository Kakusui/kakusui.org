/*
Copyright Kakusui LLC 2024 (https://kakusui.org) (https://github.com/Kakusui)
Use of this source code is governed by a GNU General Public License v3.0
license that can be found in the LICENSE file.
*/

import { Box, Button, Heading, Link, Stack, Text } from "@chakra-ui/react";
import { ExternalLinkIcon } from "@chakra-ui/icons";

function OkisouchiPage() {
    return (
        <Box p={4} bg="gray.800">
            <Heading as="h1" mb={4} color="white">Okisouchi</Heading>
            <Text mb={4} color="gray.500">
                Okisouchi is a robust, open-source tool for automating the transfer of files from Google Drive
                to designated locations, streamlining file management and organization with user-configured
                settings while ensuring data privacy and adherence to GPLv3 open-source licensing.
            </Text>
            <Link href="https://github.com/Kakusui/osc_interface" isExternal>
                <Button leftIcon={<ExternalLinkIcon />} bg="orange.400" color="white" _hover={{ bg: 'orange.500' }} variant="outline">
                    GitHub
                </Button>
            </Link>

            <Stack direction="row" spacing={4} mt={8}>
                <Link href="/okisouchi/tos" color="orange.400">Terms of Service</Link>
                <Link href="/okisouchi/privacy" color="orange.400">Privacy Policy</Link>
                <Link href="/okisouchi/license" color="orange.400">License</Link>
            </Stack>
        </Box>
    );
}

export default OkisouchiPage;