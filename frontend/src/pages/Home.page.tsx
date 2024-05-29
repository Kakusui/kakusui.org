import {
    AbsoluteCenter,
    Box,
    Button,
    chakra,
    Container,
    Divider,
    Flex,
    Grid,
    GridItem,
    Heading,
    Image,
    Stack,
    Text,
    VStack
} from "@chakra-ui/react";
import logo from '../assets/kakusui_logo.png'
import {IconBrandGithub} from "@tabler/icons-react";

function HomePage() {


    return (
        <>
            <Kakusui/>
            <Box position='relative' padding='10'>
                <Divider/>
                <AbsoluteCenter bg='gray.800' px='4'>
                    Applications
                </AbsoluteCenter>
            </Box>
            <Okisouchi/>
            <Divider mt={14} variant='dashed'/>
            <Kairyou/>
        </>
    );
}

export default HomePage;

//
// Components
//


function Kakusui() {

    return (
        <Stack direction={{base: 'column', md: 'row'}}>
            <Flex p={8} flex={1} align={'center'}>
                <Stack spacing={6} w={'full'} maxW={'xl'}>
                    <Heading fontSize={{base: '3xl', md: '4xl', lg: '5xl'}}>
                        <Text
                            as={'span'}
                            position={'relative'}
                        >
                            Kakusui
                        </Text>
                        <br/>{' '}
                        <Text color={'orange.400'} as={'span'}>
                            Innovation in translation
                        </Text>{' '}
                    </Heading>
                    <Text fontSize={{base: 'md', lg: 'lg'}} color={'gray.500'}>
                        Kakusui looks to innovate in language translation software using AI, LLMs, and new machine
                        translation technologies.
                    </Text>
                    <Stack direction={{base: 'column', md: 'row'}} spacing={4}>
                        <Button
                            rounded={'full'}
                            bg={'orange.400'}
                            color={'white'}
                            as='a' href="#applications"
                            _hover={{
                                bg: 'orange.500',
                            }}>
                            See Applications
                        </Button>
                        <Button as={'a'} href="https://github.com/Kakusui" leftIcon={<IconBrandGithub/>}
                                rounded={'full'}>Github</Button>
                    </Stack>
                </Stack>
            </Flex>
            <Flex flex={1}>
                <Image
                    boxSize={400}
                    alt={'Kakusui Logo'}
                    objectFit={'cover'}
                    src={logo}
                />
            </Flex>
        </Stack>
    );
}


function Okisouchi() {
    return (
        <Stack id="applications" direction={{base: 'column', md: 'row'}}>
            <Flex flex={1}>
                image or something?
            </Flex>
            <Flex p={8} flex={1} align={'center'}>
                <Stack spacing={6} w={'full'} maxW={'xl'}>
                    <Heading fontSize={{base: '3xl', md: '4xl', lg: '5xl'}}>
                        <Text
                            as={'span'}
                            position={'relative'}
                        >
                            Okisouchi
                        </Text>
                        <br/>{' '}
                        <Text color={'orange.400'} as={'span'}>
                            Automating the transfer of files from Google Drive
                        </Text>{' '}
                    </Heading>
                    <Text fontSize={{base: 'md', lg: 'lg'}} color={'gray.500'}>
                        Okisouchi is a robust, open-source tool for automating the transfer of files from Google Drive
                        to designated locations, streamlining file management and organization with user-configured
                        settings while ensuring data privacy and adherence to GPLv3 open-source licensing. </Text>
                    <Stack direction={{base: 'column', md: 'row'}} spacing={4}>
                        <Button
                            rounded={'full'}
                            bg={'orange.400'}
                            color={'white'}
                            _hover={{
                                bg: 'orange.500',
                            }}
                            as='a'
                            href="https://github.com/Kakusui/OSC_Interface?tab=readme-ov-file#to-use"

                        >
                            Get Started
                        </Button>
                    </Stack>
                </Stack>
            </Flex>

        </Stack>
    );
}


//
// Components: kairyou
//

interface FeatureProps {
    heading: string;
    text: string;
}

const Feature = ({heading, text}: FeatureProps) => {
    return (
        <GridItem>
            <chakra.h3 fontSize="xl" fontWeight="600">
                {heading}
            </chakra.h3>
            <chakra.p>{text}</chakra.p>
        </GridItem>
    );
};

function Kairyou() {
    return (
        <Box as={Container} maxW="7xl" mt={14} p={4}>
            <Grid
                templateColumns={{
                    base: 'repeat(1, 1fr)',
                    sm: 'repeat(2, 1fr)',
                    md: 'repeat(2, 1fr)',
                }}
                gap={4}>
                <GridItem colSpan={1}>
                    <VStack alignItems="flex-start" spacing="20px">
                        <chakra.h2 fontSize="3xl" fontWeight="700">
                            Kairyou
                        </chakra.h2>
                        <Button
                            rounded={'full'}
                            bg={'orange.400'}
                            color={'white'}
                            _hover={{
                                bg: 'orange.500',
                            }}> CTA
                        </Button>
                    </VStack>
                </GridItem>
                <GridItem>
                    <Flex>
                        <chakra.p>
                            I WILL DESCRIBE THIS PROJECT RHAHHH
                        </chakra.p>
                    </Flex>
                </GridItem>
            </Grid>
            <Divider mt={12} mb={12}/>
            <Grid
                templateColumns={{
                    base: 'repeat(1, 1fr)',
                    sm: 'repeat(2, 1fr)',
                    md: 'repeat(4, 1fr)',
                }}
                gap={{base: '8', sm: '12', md: '16'}}>
                <Feature
                    heading={'First Feature'}
                    text={'1'}
                />
                <Feature
                    heading={'Second Feature'}
                    text={'2'}
                />
                <Feature
                    heading={'Third Feature'}
                    text={'3'}
                />
                <Feature
                    heading={'Fourth Feature'}
                    text={'Short text describing one of you features/service'}
                />
            </Grid>
        </Box>

    );
}