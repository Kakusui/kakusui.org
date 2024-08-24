// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// react
import React from 'react';

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
    return (
        <>
            <Stack direction={{ base: 'column', md: reverse ? 'row-reverse' : 'row' }} mt={14}>
                <Flex flex={1}>
                    <Image boxSize={400} alt={imageAlt} objectFit="cover" src={imageUrl} borderRadius={"full"} />
                </Flex>
                <Flex p={8} flex={1} align="center">
                    <Stack spacing={6} w="full" maxW="xl">
                        <Heading fontSize={{ base: '3xl', md: '4xl', lg: '5xl' }}>
                            <Text as="span" position="relative">
                                {title}
                            </Text>
                            <br />
                            <Text color="orange.400" as="span">
                                {subtitle}
                            </Text>
                        </Heading>
                        <Text fontSize={{ base: 'md', lg: 'lg' }} color="gray.500">
                            {description}
                        </Text>
                        <Stack direction={{ base: 'column', md: 'row' }} spacing={4}>
                            <Button rounded="full" bg="orange.400" color="white" _hover={{ bg: 'orange.500' }} as="a" href={linkUrl}>
                                Try it here
                            </Button>
                            <Button as="a" href={githubUrl} leftIcon={<IconBrandGithub />} rounded="full">
                                Github
                            </Button>
                        </Stack>
                    </Stack>
                </Flex>
            </Stack>
            {features && (
                <Box as={Container} maxW="7xl" mt={14} p={4}>
                    <Divider mt={12} mb={12} />
                    <Grid templateColumns={{ base: 'repeat(1, 1fr)', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }} gap={{ base: '8', sm: '12', md: '16' }}>
                        {features.map((feature, index) => (
                            <Feature key={index} color="gray.500" heading={feature.heading} text={feature.text} />
                        ))}
                    </Grid>
                </Box>
            )}
        </>
    );
};

export default ProductSection;
