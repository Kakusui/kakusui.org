/*
Copyright Kakusui LLC 2024 (https://kakusui.org) (https://github.com/Kakusui)
Use of this source code is governed by a GNU General Public License v3.0
license that can be found in the LICENSE file.
*/

// react
import { useEffect } from 'react';

// chakra-ui
import {
    AbsoluteCenter,
    Box,
    Button,
    Divider,
    Flex,
    Heading,
    Image,
    Stack,
    Text
} from "@chakra-ui/react";

// logos and images
import logo from '../assets/images/kakusui_logo.png';
import okisouchi_sync from '../assets/images/okisouchi_sync_image.png';
import kairyou_logo from '../assets/images/kairyou_logo.png';
import easytl_logo from '../assets/images/easytl_logo.png';

// icons
import { IconBrandGithub } from '@tabler/icons-react';

// components
import ApplicationSection from "../components/ApplicationSection";

function HomePage() {

    useEffect(() => {
        document.title = 'Kakusui | Home';

    }, []);

    return (
        <>
            <Kakusui />
            <Box position="relative" padding="10">
                <Divider />
                <AbsoluteCenter bg="gray.800" px="4" id="applications">
                    Applications
                </AbsoluteCenter>
            </Box>
            <ApplicationSection
                title="EasyTL"
                subtitle="Simplifying Language Barriers with custom translation using AI and LLMs"
                description="EasyTL is a user-friendly translation tool that leverages AI and LLMs to provide high-quality translations across multiple languages. The only limit to customization is your imagination, making it a versatile tool for all your translation needs."
                imageUrl={easytl_logo}
                imageAlt="EasyTL Logo"
                linkUrl="/easytl"
                githubUrl="https://github.com/Bikatr7/EasyTL"
                features={[
                    { heading: "Powered by AI and LLMs", text: "EasyTL is powered by AI and LLMs, enabling high-quality superior translations across multiple languages." },
                    { heading: "Customizable Translation", text: "Utilizing the power of AI and LLMs, EasyTL allows customizing translations, you can set the tone, allowing different styles of translation." },
                    { heading: "Multiple Translation Options", text: "EasyTL Utilizes multiple translation options, such as OpenAI, Anthropic, and Gemini, to provide a wide range of translation options." },
                    { heading: "Quick and Easy to Use", text: "EasyTL is user-friendly, making it easy to use, with a simple interface that allows users to quickly translate text." }
                ]}
            />
            <Divider mt={14} variant="dashed" />
            <ApplicationSection
                title="Kairyou"
                subtitle="Quickly preprocess Japanese text using NLP/NER from SpaCy for Japanese translation or other NLP tasks."
                description="Kairyou is a Japanese text preprocessing tool that uses SpaCy to automatically replace named entities with placeholders, making it easier to translate or analyze Japanese text. It also supports name indexing for discovering new named entities and can be used for other NLP tasks."
                imageUrl={kairyou_logo}
                imageAlt="Kairyou Logo"
                linkUrl="/kairyou"
                githubUrl="https://github.com/Bikatr7/Kairyou"
                reverse
                features={[
                    { heading: "Advanced Japanese NLP", text: "Leverages SpaCy's NLP capabilities to provide robust preprocessing of Japanese text, including named entity recognition and tokenization." },
                    { heading: "Translation preparation", text: "Automatically replaces named entities with placeholders, making it easier to translate Japanese text." },
                    { heading: "Katakana Utility", text: "Includes versatile utilities such as KatakanaUtil for specialized text manipulation, allowing users to tailor preprocessing to specific needs." },
                    { heading: "Name Indexing", text: "Supports name indexing for discovering new named entities, which can be used for other NLP tasks." }
                ]}
            />
            <Divider mt={14} variant="dashed" />
            <ApplicationSection
                title="Okisouchi"
                subtitle="Automating the transfer of files from Google Drive"
                description="Okisouchi is a robust, open-source tool for automating the transfer of files from Google Drive to designated locations, streamlining file management and organization with user-configured settings while ensuring data privacy and adherence to GPLv3 open-source licensing."
                imageUrl={okisouchi_sync}
                imageAlt="Okisouchi Sync"
                linkUrl="/okisouchi"
                githubUrl="https://github.com/Kakusui"
            />
        </>
    );
}

export default HomePage;

//
// Components
//

function Kakusui() {
    return (
        <Stack direction={{ base: 'column', md: 'row' }}>
            <Flex p={8} flex={1} align="center">
                <Stack spacing={6} w="full" maxW="xl">
                    <Heading fontSize={{ base: '3xl', md: '4xl', lg: '5xl' }}>
                        <Text as="span" position="relative">
                            Kakusui
                        </Text>
                        <br />
                        <Text color="orange.400" as="span">
                            Innovation in translation
                        </Text>
                    </Heading>
                    <Text fontSize={{ base: 'md', lg: 'lg' }} color="gray.500">
                        Kakusui looks to innovate in language translation using AI, LLMs, and new machine translation technologies.
                    </Text>
                    <Stack direction={{ base: 'column', md: 'row' }} spacing={4}>
                        <Button rounded="full" bg="orange.400" color="white" as="a" href="#applications" _hover={{ bg: 'orange.500' }}>
                            See Applications
                        </Button>
                        <Button as="a" href="https://github.com/Kakusui" leftIcon={<IconBrandGithub />} rounded="full">
                            Github
                        </Button>
                    </Stack>
                </Stack>
            </Flex>
            <Flex flex={1}>
                <Image boxSize={400} alt="Kakusui Logo" objectFit="cover" src={logo} />
            </Flex>
        </Stack>
    );
}