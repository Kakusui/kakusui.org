import { Box, Link, Stack } from '@chakra-ui/react';

interface LegalLinksProps {
    basePath: string;
}

const LegalLinks: React.FC<LegalLinksProps> = ({ basePath }) => {
    return (
        <Box mt={5} p={2} bg="gray.800">
            <Stack direction="row">
                <Link href={`${basePath}/tos`} color="orange.400">Terms of Service</Link>
                <Link href={`${basePath}/privacy`} color="orange.400">Privacy Policy</Link>
                <Link href={`${basePath}/license`} color="orange.400">License</Link>
            </Stack>
        </Box>
    );
};

export default LegalLinks;
