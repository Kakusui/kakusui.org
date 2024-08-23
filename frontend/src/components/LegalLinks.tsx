/*
Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
Use of this source code is governed by an GNU Affero General Public License v3.0
license that can be found in the LICENSE file.
*/

import { Box, Link, Stack } from '@chakra-ui/react';

interface LegalLinksProps {
    basePath: string;
}

const LegalLinks: React.FC<LegalLinksProps> = ({ basePath }) => {
    return (
        <Box mt={5} p={2} bg="#14192b">
            <Stack direction="row">
                <Link href={`${basePath}/tos`} color="orange.400">Terms of Service</Link>
                <Link href={`${basePath}/privacy`} color="orange.400">Privacy Policy</Link>
                <Link href={`${basePath}/license`} color="orange.400">License</Link>
            </Stack>
        </Box>
    );
};

export default LegalLinks;
