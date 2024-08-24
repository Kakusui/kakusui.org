// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// chakra-ui
import { Box } from '@chakra-ui/react';

// components
import FooterContent from './FooterContent';

function Footer() 
{
    return (
        <Box
            bg="#14192b"
            color="gray.300"
            borderTop="1px"
            borderColor="rgba(255, 255, 255, 0.1)"
            boxShadow="0 -1px 2px 0 rgba(0, 0, 0, 0.05)"
            width="100%"
            mt={6}
        >
            <FooterContent />
        </Box>
    );
}

export default Footer;