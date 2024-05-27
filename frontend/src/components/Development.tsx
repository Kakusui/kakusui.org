import {Box, Heading, Text} from '@chakra-ui/react';
import {WarningTwoIcon} from '@chakra-ui/icons';

function Development() {

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

export default Development;