/*
Copyright Kakusui LLC 2024 (https://kakusui.org) (https://github.com/Kakusui)
Use of this source code is governed by a GNU General Public License v3.0
license that can be found in the LICENSE file.
*/

// chakra-ui
import {
    AbsoluteCenter,
    Box,
    Button,
    Container,
    Divider,
    Flex,
    Grid,
    Heading,
    Image,
    Stack,
    Text
} from "@chakra-ui/react";

// logos and images
import logo from '../assets/kakusui_logo.png'
import okisouchi_sync from '../assets/okisouchi_sync_image.png'
import kairyou_logo from '../assets/kairyou_logo.png'

// icons
import {IconBrandGithub} from "@tabler/icons-react";

// components
import Feature from "../components/Feature";

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
            <Kairyou/>
            <Divider mt={14} variant='dashed'/>
            <Okisouchi/>

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
                        Kakusui looks to innovate in language translation using AI, LLMs, and new machine
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
                <Image
                    boxSize={400}
                    alt={'Okisouchi Sync'}
                    objectFit={'cover'}
                    src={okisouchi_sync}
                />
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
                            href="/okisouchi"

                        >
                            See more
                        </Button>
                    </Stack>
                </Stack>
            </Flex>
        </Stack>
    );
}

function Kairyou() {
    return (
        <>
            <Stack direction={{base: 'column', md: 'row'}} mt={14}>
                <Flex p={8} flex={1} align={'center'}>
                    <Stack spacing={6} w={'full'} maxW={'xl'}>
                        <Heading fontSize={{base: '3xl', md: '4xl', lg: '5xl'}}>
                            <Text
                                as={'span'}
                                position={'relative'}
                            >
                                Kairyou
                            </Text>
                            <br/>{' '}
                            <Text color={'orange.400'} as={'span'}>
                                Quickly preprocess Japanese text using NLP/NER from SpaCy for Japanese translation or other NLP tasks. 
                            </Text>{' '}
                        </Heading>
                        <Text fontSize={{base: 'md', lg: 'lg'}} color={'gray.500'}>
                            Kairyou is a Japanese text preprocessing tool that uses SpaCy to automatically replace named entities with placeholders, making it easier to translate or analyze Japanese text.
                            It also supports name indexing for discovering new named entities and can be used for other NLP tasks.
                        </Text>
                        <Stack direction={{base: 'column', md: 'row'}} spacing={4}>
                            <Button
                                rounded={'full'}
                                bg={'orange.400'}
                                color={'white'}
                                _hover={{
                                    bg: 'orange.500',
                                }}
                                as='a'
                                href="/kairyou"
                            >
                                Try it here
                            </Button>
                            <Button as={'a'} href="https://github.com/Bikatr7/Kairyou" leftIcon={<IconBrandGithub/>}
                                    rounded={'full'}>Github</Button>
                        </Stack>
                    </Stack>
                </Flex>
                <Flex flex={1}>
                    <Image
                        boxSize={400}
                        alt={'Kairyou Logo'}
                        objectFit={'cover'}
                        src={kairyou_logo}
                    />
                </Flex>
            </Stack>
            <Box as={Container} maxW="7xl" mt={14} p={4}>
                <Divider mt={12} mb={12}/>
                <Grid
                    templateColumns={{
                        base: 'repeat(1, 1fr)',
                        sm: 'repeat(2, 1fr)',
                        md: 'repeat(4, 1fr)',
                    }}
                    gap={{base: '8', sm: '12', md: '16'}}>
                    <Feature
                        heading={'Advanced Japanese NLP'}
                        text={"Leverages SpaCy's NLP capabilities to provide robust preprocessing of Japanese text, including named entity recognition and tokenization."}
                    />
                    <Feature
                        heading={'Translation preparation'}
                        text={'Automatically replaces named entities with placeholders, making it easier to translate Japanese text.'}
                    />
                    <Feature
                        heading={'Katakana Utility'}
                        text={"Includes versatile utilities such as KatakanaUtil for specialized text manipulation, allowing users to tailor preprocessing to specific needs."}
                    />
                    <Feature
                        heading={'Name Indexing'}
                        text={'Supports name indexing for discovering new named entities, which can be used for other NLP tasks.'}
                    />
                </Grid>
            </Box>
        </>
    );
}