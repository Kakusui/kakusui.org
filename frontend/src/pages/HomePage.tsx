// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// react
import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

// motion
import { motion } from 'framer-motion';

// chakra-ui
import { useDisclosure, AbsoluteCenter, Box, Button, Divider, Flex, Heading, Image, Modal, ModalBody, ModalCloseButton, ModalContent, ModalHeader, ModalOverlay, Stack, Text } from "@chakra-ui/react";

// logos and images
import logo from '../assets/images/kakusui_logo.webp';
import kairyou_logo from '../assets/images/kairyou_logo.webp';
import easytl_logo from '../assets/images/easytl_logo.webp';
import elucidate_logo from '../assets/images/elucidate_logo.webp';

// icons
import { IconBrandGithub } from '@tabler/icons-react';

// components
import ProductSection from "../components/ProductSection";
import PageWrapper from "../components/PageWrapper";
import HomeHeader from "../components/HomeHeader";
import HomeFooter from "../components/HomeFooter";
import Login from '../components/Login';

// animations
import { textVariants, containerVariants, imageVariants, buttonVariants, githubButtonVariants } from '../animations/commonAnimations';

import { getURL } from '../utils';

function HomePage() 
{
    const { isOpen, onOpen, onClose } = useDisclosure();
    const [isMobile, setIsMobile] = useState(false);
    const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
    const location = useLocation();
    const navigate = useNavigate();

    useEffect(() => 
    {
        document.title = 'Kakusui | Home';

        const checkMobile = () => {
            setIsMobile(window.innerWidth <= 768);
        };

        checkMobile();
        window.addEventListener('resize', checkMobile);

        const shouldShowModal = localStorage.getItem('hideMobileModalWarningPersistent') !== 'true';
        if (isMobile && shouldShowModal) {
            onOpen();
        }

        const searchParams = new URLSearchParams(location.search);
        if (searchParams.get('openLoginModal') === 'true') {
            setIsLoginModalOpen(true);
        }

        return () => window.removeEventListener('resize', checkMobile);
    }, [onOpen, isMobile, location]);

    const handleDoNotShowAgain = () => {
        localStorage.setItem('hideMobileModalWarningPersistent', 'true');
        onClose();
    };

    const handleLoginModalOpen = () => {
        setIsLoginModalOpen(true);
    };

    const checkLoginStatusAndRedirect = async () => {
        try {
            const response = await fetch(getURL('/auth/verify-token'), {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                },
            });
            const data = await response.json();
            
            if (data.valid) 
            {
                const searchParams = new URLSearchParams(location.search);
                const redirectPath = searchParams.get('redirect');
                if (redirectPath) 
                {
                    navigate(redirectPath, { replace: true });
                } else {
                    navigate(location.pathname, { replace: true });
                }
            } 
            else 
            {
                navigate(location.pathname, { replace: true });
            }
        } catch (error) {
            navigate(location.pathname, { replace: true });
        }
    };

    const handleLoginModalClose = () => {
        setIsLoginModalOpen(false);
        // Check login status and redirect after a short delay
        setTimeout(checkLoginStatusAndRedirect, 500);
    };

    return (
        <PageWrapper showBackground={true}>
            <HomeHeader onLoginClick={handleLoginModalOpen} />
            <Box px={4} pt="60px" pb="100px">
                <Kakusui />
                <Box position="relative" padding="10">
                    <Divider />
                    <AbsoluteCenter bg="#14192b" px="4" id="products">
                        Products
                    </AbsoluteCenter>
                </Box>                
                <ProductSection
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
                <ProductSection
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
                <ProductSection
                    title="Elucidate"
                    subtitle="Smarter Translations through LLM Self-Evaluation"
                    description="Elucidate is a tool to that allows for the evaluation of translation utilizing LLMs. It provides insights into the quality of translations and allows for customizable evaluation options, making it a versatile tool for all your translation needs."
                    imageUrl={elucidate_logo}
                    imageAlt="Elucidate Logo"
                    linkUrl="/elucidate"
                    githubUrl="https://github.com/Kakusui/Elucidate"
                    features={[
                        { heading: "LLM Self-Evaluation", text: "Elucidate allows users to evaluate translations using LLMs, providing insights into the quality of translations." },
                        { heading: "Customizable Evaluation", text: "Users can customize the evaluation process, allowing for a wide range of evaluation options." },
                        { heading: "Multiple LLM Options", text: "Elucidate supports multiple LLMs, including OpenAI, Anthropic, and Gemini, providing a wide range of evaluation options." },
                        { heading: "User-Friendly Interface", text: "Elucidate is user-friendly, with a simple interface that allows users to quickly evaluate translations." }
                    ]}
                />
            </Box>
            <HomeFooter />

            <Modal isOpen={isOpen} onClose={onClose} motionPreset="slideInBottom" isCentered>
                <ModalOverlay />
                <ModalContent
                    borderRadius="md"
                    bg="blue.900"
                    color="white"
                >
                    <ModalHeader color="orange.400">Recommendation</ModalHeader>
                    <ModalCloseButton />
                    <ModalBody pb={6}>
                        <Text>
                            For the best experience, we recommend using kakusui.org on a computer. 
                            The mobile version may have limited functionality.
                        </Text>
                    </ModalBody>
                    <Flex justifyContent="flex-end" p={4}>
                        <Button colorScheme="orange" mr={3} onClick={onClose}>
                            Okay
                        </Button>
                        <Button variant="outline" colorScheme="orange" onClick={handleDoNotShowAgain}>
                            Do not show again
                        </Button>
                    </Flex>
                </ModalContent>
            </Modal>

            <Login 
                isOpen={isLoginModalOpen} 
                onClose={handleLoginModalClose} 
                hidden={true} // Set hidden to true for HomePage
            />
        </PageWrapper>
    );
}

export default HomePage;

function Kakusui() 
{
    return  (
        <Stack direction={{ base: 'column', md: 'row' }} spacing={8}>
            <Flex p={8} flex={1} align="center">
                <motion.div
                    initial="hidden"
                    animate="visible"
                    variants={containerVariants}
                >
                    <Stack spacing={6} w="full" maxW="xl">
                        <motion.div variants={textVariants}>
                            <Heading fontSize={{ base: '3xl', md: '4xl', lg: '5xl' }}>
                                <Text as="span" position="relative">
                                    Kakusui
                                </Text>
                                <br />
                                <Text color="orange.400" as="span">
                                    Innovation in translation
                                </Text>
                            </Heading>
                        </motion.div>
                        <motion.div variants={textVariants}>
                            <Text fontSize={{ base: 'md', lg: 'lg' }} color="gray.500">
                                Kakusui looks to innovate in language translation using AI, LLMs, and new machine translation technologies.
                            </Text>
                        </motion.div>
                        <motion.div variants={textVariants}>
                            <Stack direction={{ base: 'column', md: 'row' }} spacing={4}>
                                <motion.div whileHover="hover" variants={buttonVariants}>
                                    <Button rounded="full" bg="orange.400" color="white" as="a" href="#products" _hover={{ bg: 'orange.500' }}>
                                        See Products
                                    </Button>
                                </motion.div>
                                <motion.div whileHover="hover" variants={githubButtonVariants}>
                                    <Button as="a" href="https://github.com/Kakusui" leftIcon={<IconBrandGithub />} rounded="full">
                                        Github
                                    </Button>
                                </motion.div>
                            </Stack>
                        </motion.div>
                    </Stack>
                </motion.div>
            </Flex>
            <Flex flex={1} justifyContent="center" alignItems="center">
                <motion.div whileHover="hover" variants={imageVariants}>
                    <Image 
                        boxSize={{ base: "300px", md: "400px" }} 
                        alt="Kakusui Logo" 
                        objectFit="cover" 
                        src={logo} 
                        borderRadius={"full"}
                    />
                </motion.div>
            </Flex>
        </Stack>
    );
}
