/*
Copyright Kakusui LLC 2024 (https://kakusui.org) (https://github.com/Kakusui)
Use of this source code is governed by a GNU General Public License v3.0
license that can be found in the LICENSE file.
*/

import {Box, Heading, Text} from '@chakra-ui/react';
import {WarningTwoIcon} from '@chakra-ui/icons';

function DevelopmentBanner() 
{

    return (
        <Box textAlign="start" py={10} px={6}>
            <WarningTwoIcon boxSize={'50px'} color={'orange.300'}/>
            <Heading as="h2" size="xl" mt={6} mb={2}>
                In-development
            </Heading>
            <Text color={'gray.500'}>
                Welcome to our website, we're working on a lot right now, more to come soon!
            </Text>
        </Box>)
}

export default DevelopmentBanner;