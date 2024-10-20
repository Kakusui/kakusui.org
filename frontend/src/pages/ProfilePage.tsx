// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// react
import React, { useEffect, useState } from 'react';

// chakra-ui
import {
    Box,
    Heading,
    Text,
    VStack,
    Spinner,
    useToast,
    Card,
    CardHeader,
    CardBody,
    Flex,
    Avatar,
    Badge,
    Divider
} from '@chakra-ui/react';

// auth
import { useAuth } from '../contexts/AuthContext';

// utils
import { getURL } from '../utils';

interface UserInfo 
{
    id: string;
    email: string;
    credits: number;
}

const ProfilePage: React.FC = () => 
{
    const { isLoggedIn, userEmail } = useAuth();
    const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const toast = useToast();

    useEffect(() => 
    {
        const fetchUserInfo = async () => 
        {
            if (!isLoggedIn || !userEmail) 
            {
                setIsLoading(false);
                return;
            }

            try 
            {
                const response = await fetch(getURL('/user/info'), 
                {
                    method: 'GET',
                    headers: 
                    {
                        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                        'Content-Type': 'application/json'
                    }
                });

                if (response.ok) 
                {
                    const data = await response.json();
                    setUserInfo(data);
                } 
                else 
                {
                    throw new Error('Failed to fetch user info');
                }
            } 
            catch (error) 
            {
                console.error('Error fetching user info:', error);
                toast(
                {
                    title: "Error",
                    description: "Failed to load user information",
                    status: "error",
                    duration: 5000,
                    isClosable: true,
                });
            } 
            finally 
            {
                setIsLoading(false);
            }
        };

        fetchUserInfo();
    }, [isLoggedIn, userEmail, toast]);

    if (!isLoggedIn) 
    {
        return (
            <Box p={8} maxWidth="container.md" margin="auto">
                <Card bg="gray.800" color="white">
                    <CardBody>
                        <Heading size="lg" mb={4}>Profile</Heading>
                        <Text>Please log in to view your profile.</Text>
                    </CardBody>
                </Card>
            </Box>
        );
    }

    if (isLoading) 
    {
        return (
            <Box p={8} display="flex" justifyContent="center" alignItems="center" height="200px">
                <Spinner size="xl" color="orange.400" />
            </Box>
        );
    }

    return (
        <Box p={8} maxWidth="container.md" margin="auto">
            <Card bg="gray.800" color="white">
                <CardHeader>
                    <Flex>
                        <Flex flex="1" gap="4" alignItems="center" flexWrap="wrap">
                            <Avatar name={userInfo?.email} bg="orange.400" />
                            <Box>
                                <Heading size="md">{userInfo?.email}</Heading>
                                <Badge colorScheme="orange">User</Badge>
                            </Box>
                        </Flex>
                    </Flex>
                </CardHeader>
                <CardBody>
                    <VStack align="start" spacing={4}>
                        <Box>
                            <Text fontWeight="bold" mb={1}>Email</Text>
                            <Text>{userInfo?.email}</Text>
                        </Box>
                        <Divider />
                        <Box>
                            <Text fontWeight="bold" mb={1}>Credits</Text>
                            <Text>{userInfo?.credits}</Text>
                        </Box>
                        <Divider />
                        <Box>
                            <Text fontWeight="bold" mb={1}>User ID</Text>
                            <Text fontSize="sm" color="gray.400">{userInfo?.id}</Text>
                        </Box>
                    </VStack>
                </CardBody>
            </Card>
        </Box>
    );
};

export default ProfilePage;