// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// react
import React from 'react';

// chakra-ui
import { Box } from "@chakra-ui/react";

// images
import landingPageBg from '../assets/images/landing_page.webp';

interface PageWrapperProps 
{
    children: React.ReactNode;
    showBackground?: boolean;
    zIndex?: number;
}

function PageWrapper({ children, showBackground = false, zIndex = 1 }: PageWrapperProps) 
{
    return (
        <Box
            position="relative"
            minHeight="100vh"
            backgroundImage={showBackground ? `url(${landingPageBg})` : 'none'}
            backgroundSize="cover"
            backgroundPosition="center"
            backgroundAttachment="fixed"
            zIndex={zIndex}
        >
            {showBackground && (
                <Box
                    position="absolute"
                    top="0"
                    left="0"
                    right="0"
                    bottom="0"
                    backgroundColor="rgba(0, 0, 0, 0.7)"
                    zIndex={zIndex - 1}
                />
            )}
            <Box
                position="relative"
                maxWidth="container.xl"
                margin="0 auto"
                backgroundColor="#14192b"
                minHeight="100vh"
                px={4}
                zIndex={zIndex}
            >
                {children}
            </Box>
        </Box>
    );
}

export default PageWrapper;