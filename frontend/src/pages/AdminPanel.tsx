// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// react
import { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';

// chakra-ui
import { Box, Button, Heading, Input, Textarea, useToast, Text, HStack, Divider, Tab, TabList, TabPanel, TabPanels, Tabs } from "@chakra-ui/react";

// images
import landingPageBg from '../assets/images/landing_page.webp';

// util
import { getURL } from '../utils';

function AdminPanel() 
{
    const [emailSubject, setEmailSubject] = useState('');
    const [emailBody, setEmailBody] = useState('');
    const [sqlQuery, setSqlQuery] = useState('');
    const [queryResult, setQueryResult] = useState('');
    const toast = useToast();
    const modalRef = useRef<HTMLDivElement>(null);
    const [modalSize, setModalSize] = useState(() => {
        const savedSize = localStorage.getItem('adminPanelSize');
        return savedSize ? JSON.parse(savedSize) : { width: 800, height: 600 };
    });
    const [modalPosition, setModalPosition] = useState(() => {
        const savedPosition = localStorage.getItem('adminPanelPosition');
        return savedPosition ? JSON.parse(savedPosition) : { left: window.innerWidth / 2, top: window.innerHeight / 2 };
    });

    const handleSendEmail = async () => 
    {
        try 
        {
            const response = await fetch(getURL('/admin/send-email'), 
            {
                method: 'POST',
                headers: 
                {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({ subject: emailSubject, body: emailBody })
            });

            if (response.ok) 
            {
                toast({
                    title: "Emails Sent",
                    description: "The emails have been sent to all users successfully.",
                    status: "success",
                    duration: 5000,
                    isClosable: true,
                });
                setEmailSubject('');
                setEmailBody('');
            } 
            else 
            {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Failed to send emails');
            }
        } 
        catch (error) 
        {
            toast({
                title: "Error",
                description: (error as Error).message || "Failed to send emails. Please try again.",
                status: "error",
                duration: 5000,
                isClosable: true,
            });
        }
    };

    const handleRunQuery = async () => 
    {
        try 
        {
            const response = await fetch(getURL('/admin/run-query'), 
            {
                method: 'POST',
                headers: 
                {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({ query: sqlQuery })
            });

            if (response.ok) 
            {
                const result = await response.json();
                setQueryResult(JSON.stringify(result, null, 2));
                toast({
                    title: "Query Executed",
                    description: "The query has been executed successfully.",
                    status: "success",
                    duration: 5000,
                    isClosable: true,
                });
            } 
            else 
            {
                throw new Error('Failed to run query');
            }
        } 
        catch (error) 
        {
            toast({
                title: "Error",
                description: "Failed to run query. Please try again.",
                status: "error",
                duration: 5000,
                isClosable: true,
            });
        }
    };

    const handleDrag = (e: React.MouseEvent<HTMLDivElement>) => 
    {
        // Prevent dragging when clicking on the resize handle
        if ((e.target as HTMLElement).closest('.resize-handle')) return;

        const modal = modalRef.current;
        if (!modal) return;

        const startX = e.clientX - modalPosition.left;
        const startY = e.clientY - modalPosition.top;

        const onMouseMove = (e: MouseEvent) => 
        {
            const newLeft = e.clientX - startX;
            const newTop = e.clientY - startY;

            setModalPosition({ left: newLeft, top: newTop });
        };

        const onMouseUp = () => 
        {
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
        };

        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
    };

    const handleResize = (e: React.MouseEvent<HTMLDivElement>) => 
    {
        const modal = modalRef.current;
        if (!modal) return;

        const startX = e.clientX;
        const startY = e.clientY;
        const startWidth = modal.offsetWidth;
        const startHeight = modal.offsetHeight;

        const onMouseMove = (e: MouseEvent) => 
        {
            const newWidth = startWidth + e.clientX - startX;
            const newHeight = startHeight + e.clientY - startY;

            const updatedSize = {
                width: Math.max(400, Math.min(newWidth, window.innerWidth)),
                height: Math.max(300, Math.min(newHeight, window.innerHeight))
            };
            setModalSize(updatedSize);
        };

        const onMouseUp = () => 
        {
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
        };

        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
    };

    const resetModalSizeAndPosition = () => 
    {
        const defaultSize = { width: 800, height: 600 };
        const defaultPosition = { left: window.innerWidth / 2, top: window.innerHeight / 2 };
        setModalSize(defaultSize);
        setModalPosition(defaultPosition);
        localStorage.removeItem('adminPanelSize');
        localStorage.removeItem('adminPanelPosition');
    };

    useEffect(() => 
    {
        const handleKeyDown = (e: KeyboardEvent) => 
        {
            if (e.altKey && e.key === 'r') 
            {
                resetModalSizeAndPosition();
            }
        };

        window.addEventListener('keydown', handleKeyDown);

        return () => 
        {
            window.removeEventListener('keydown', handleKeyDown);
        };
    }, []);

    useEffect(() => 
    {
        localStorage.setItem('adminPanelSize', JSON.stringify(modalSize));
    }, [modalSize]);

    useEffect(() => 
    {
        localStorage.setItem('adminPanelPosition', JSON.stringify(modalPosition));
    }, [modalPosition]);

    useEffect(() => 
    {
        const modal = modalRef.current;
        if (modal) 
        {
            modal.style.width = `${modalSize.width}px`;
            modal.style.height = `${modalSize.height}px`;
            modal.style.left = `${modalPosition.left}px`;
            modal.style.top = `${modalPosition.top}px`;
        }
    }, [modalSize, modalPosition]);

    return (
        <Box
            height="100vh"
            width="100vw"
            position="relative"
            overflow="hidden"
        >
            <Box
                position="absolute"
                top="0"
                left="0"
                right="0"
                bottom="0"
                backgroundImage={`url(${landingPageBg})`}
                backgroundSize="cover"
                backgroundPosition="center"
                filter="brightness(0.6)"
            />
            <Box
                ref={modalRef}
                position="absolute"
                left={`${modalPosition.left}px`}
                top={`${modalPosition.top}px`}
                transform="translate(-50%, -50%)"
                bg="rgba(20, 25, 43, 0.95)"
                p={4}
                borderRadius="xl"
                color="white"
                boxShadow="0 4px 6px rgba(0, 0, 0, 0.1)"
                width={`${modalSize.width}px`}
                height={`${modalSize.height}px`}
                display="flex"
                flexDirection="column"
                overflow="hidden"
                onMouseDown={handleDrag}
                cursor="move"
            >
                <HStack justifyContent="space-between" mb={2}>
                    <Heading size="lg" color="orange.400" userSelect="none">Admin Panel</Heading>
                    <Link to="/home">
                        <Text color="orange.400" cursor="pointer" userSelect="none">Go Back</Text>
                    </Link>
                </HStack>
                <Divider mb={2} />
                <Tabs variant="enclosed" colorScheme="orange" flex={1} display="flex" flexDirection="column">
                    <TabList>
                        <Tab>Email</Tab>
                        <Tab>Query</Tab>
                    </TabList>
                    <TabPanels flex={1} overflow="hidden">
                        <TabPanel height="100%" display="flex" flexDirection="column">
                            <Input
                                placeholder="Email Subject"
                                value={emailSubject}
                                onChange={(e) => setEmailSubject(e.target.value)}
                                mb={2}
                            />
                            <Textarea
                                placeholder="Email Body"
                                value={emailBody}
                                onChange={(e) => setEmailBody(e.target.value)}
                                mb={2}
                                flex={1}
                                resize="none"
                            />
                            <Button onClick={handleSendEmail} colorScheme="orange">Send Email to All</Button>
                        </TabPanel>
                        <TabPanel height="100%" display="flex" flexDirection="column">
                            <Textarea
                                placeholder="Enter SQL Query"
                                value={sqlQuery}
                                onChange={(e) => setSqlQuery(e.target.value)}
                                mb={2}
                                flex={1}
                                resize="none"
                            />
                            <Button onClick={handleRunQuery} colorScheme="orange" mb={2}>Run Query</Button>
                            {queryResult && (
                                <Box
                                    flex={1}
                                    p={2}
                                    bg="whiteAlpha.100"
                                    borderRadius="md"
                                    fontSize="sm"
                                    fontFamily="monospace"
                                    whiteSpace="pre-wrap"
                                    overflow="hidden"
                                >
                                    {queryResult}
                                </Box>
                            )}
                        </TabPanel>
                    </TabPanels>
                </Tabs>
                <Box
                    position="absolute"
                    bottom="0"
                    right="0"
                    width="20px"
                    height="20px"
                    cursor="se-resize"
                    onMouseDown={handleResize}
                    className="resize-handle"
                />
            </Box>
        </Box>
    );
}

export default AdminPanel;