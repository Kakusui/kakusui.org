/*
Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
Use of this source code is governed by a GNU General Public License v3.0
license that can be found in the LICENSE file.
*/

import { useEffect } from 'react';
import { Box, Button, Heading, Link, Stack, Text } from "@chakra-ui/react";
import { ExternalLinkIcon } from "@chakra-ui/icons";

function ElucidatePage() 
{
    useEffect(() => {
        document.title = 'Kakusui | Elucidate';

    }, []);

    return (
        <Box p={4} bg="gray.800">
            <Heading as="h1" mb={4} color="white">Elucidate</Heading>
            <Text mb={4} color="gray.500">
                Elucidate is an upcoming project that aims to bring clarity and innovation to translation. Stay tuned for more details and updates as we work towards launching this exciting new tool.
            </Text>
            <Link href="https://github.com/Kakusui/Elucidate" isExternal>
                <Button leftIcon={<ExternalLinkIcon />} bg="orange.400" color="white" _hover={{ bg: 'orange.500' }} variant="outline">
                    GitHub
                </Button>
            </Link>

            <Stack direction="row" spacing={4} mt={8}>
                <Link href="/elucidate/tos" color="orange.400">Terms of Service</Link>
                <Link href="/elucidate/privacy" color="orange.400">Privacy Policy</Link>
                <Link href="/elucidate/license" color="orange.400">License</Link>
            </Stack>
        </Box>
    );
}

export default ElucidatePage;
