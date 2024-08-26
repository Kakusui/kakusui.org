// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// react
import React from 'react';

// chakra-ui
import { Box, Divider } from '@chakra-ui/react';

// components
import FooterContent from './FooterContent';

const HomeFooter: React.FC = () => 
{
    return (
        <Box
            position="absolute"
            bottom={0}
            left={0}
            right={0}
            bg="transparent"
            color="white"
            py={4}
            zIndex={1}
            marginTop={10}
        >
            <Divider borderColor="rgba(255, 255, 255, 0.1)" mb={4} />
            <FooterContent color="white" />
        </Box>
    );
};

export default HomeFooter;