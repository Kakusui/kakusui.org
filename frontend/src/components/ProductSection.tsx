// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// react
import React from 'react';
import { motion } from 'framer-motion';

// chakra-ui
import { Stack, Flex, Image, Heading, Text, Button, Box, Container, Divider, Grid } from '@chakra-ui/react';

// icons
import { IconBrandGithub } from "@tabler/icons-react";

// components
import Feature from "./Feature";

interface ProductSectionProps 
{
    title: string;
    subtitle: string;
    description: string;
    imageUrl: string;
    imageAlt: string;
    linkUrl: string;
    githubUrl: string;
    features?: { heading: string, text: string }[];
    reverse?: boolean;
}

const ProductSection: React.FC<ProductSectionProps> = ({ title, subtitle, description, imageUrl, imageAlt, linkUrl, githubUrl, features, reverse }) => 
{
    const containerVariants = 
    {
        hidden: { opacity: 0, x: reverse ? 50 : -50 },
        visible: 
        { 
            opacity: 1, 
            x: 0,
            transition: 
            { 
                duration: 0.5, 
                ease: "easeOut",
                staggerChildren: 0.2
            }
        }
    };

    const textVariants = 
    {
        hidden: { opacity: 0, y: 20 },
        visible: 
        { 
            opacity: 1, 
            y: 0,
            transition: { duration: 0.5, ease: "easeOut" }
        }
    };

    const imageVariants = 
    {
        hover: 
        { 
            scale: 1.05,
            transition: { duration: 0.3 }
        }
    };

    const buttonVariants = 
    {
        hover: 
        { 
            scale: 1.05,
            transition: 
            { 
                duration: 0.3,
                yoyo: Infinity
            }
        }
    };

    const githubButtonVariants = 
    {
        hover: 
        { 
            x: [0, 5, 0],
            transition: 
            { 
                duration: 0.5,
                repeat: Infinity
            }
        }
    };

    return (
        <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.3 }}
            variants={containerVariants}
        >
            <Stack direction={{ base: 'column', md: reverse ? 'row-reverse' : 'row' }} mt={14}>
                <Flex flex={1}>
                    <motion.div whileHover="hover" variants={imageVariants}>
                        <Image boxSize={400} alt={imageAlt} objectFit="cover" src={imageUrl} borderRadius={"full"} />
                    </motion.div>
                </Flex>
                <Flex p={8} flex={1} align="center">
                    <Stack spacing={6} w="full" maxW="xl">
                        <motion.div variants={textVariants}>
                            <Heading fontSize={{ base: '3xl', md: '4xl', lg: '5xl' }}>
                                <Text as="span" position="relative">
                                    {title}
                                </Text>
                                <br />
                                <Text color="orange.400" as="span">
                                    {subtitle}
                                </Text>
                            </Heading>
                        </motion.div>
                        <motion.div variants={textVariants}>
                            <Text fontSize={{ base: 'md', lg: 'lg' }} color="gray.500">
                                {description}
                            </Text>
                        </motion.div>
                        <motion.div variants={textVariants}>
                            <Stack direction={{ base: 'column', md: 'row' }} spacing={4}>
                                <motion.div whileHover="hover" variants={buttonVariants}>
                                    <Button rounded="full" bg="orange.400" color="white" _hover={{ bg: 'orange.500' }} as="a" href={linkUrl}>
                                        Try it here
                                    </Button>
                                </motion.div>
                                <motion.div whileHover="hover" variants={githubButtonVariants}>
                                    <Button as="a" href={githubUrl} leftIcon={<IconBrandGithub />} rounded="full">
                                        Github
                                    </Button>
                                </motion.div>
                            </Stack>
                        </motion.div>
                    </Stack>
                </Flex>
            </Stack>
            {features && (
                <Box as={Container} maxW="7xl" mt={14} p={4}>
                    <Divider mt={12} mb={12} />
                    <Grid templateColumns={{ base: 'repeat(1, 1fr)', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }} gap={{ base: '8', sm: '12', md: '16' }}>
                        {features.map((feature, index) => (
                            <motion.div key={index} variants={textVariants}>
                                <Feature color="gray.500" heading={feature.heading} text={feature.text} />
                            </motion.div>
                        ))}
                    </Grid>
                </Box>
            )}
        </motion.div>
    );
};

export default ProductSection;