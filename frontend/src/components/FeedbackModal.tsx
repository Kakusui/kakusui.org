// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// react
import { useState, useEffect } from 'react';

// chakra-ui
import {
    Modal,
    ModalOverlay,
    ModalContent,
    ModalHeader,
    ModalFooter,
    ModalBody,
    ModalCloseButton,
    Button,
    Input,
    Textarea,
    VStack,
    Text,
    Checkbox,
    useToast
} from '@chakra-ui/react';

// utils
import { getURL } from '../utils';

// auth
import { useAuth } from '../contexts/AuthContext';

interface FeedbackModalProps
{
    isOpen: boolean;
    onClose: () => void;
}

const FeedbackModal: React.FC<FeedbackModalProps> = ({ isOpen, onClose }) =>
{
    const [email, setEmail] = useState('');
    const [feedback, setFeedback] = useState('');
    const [agreeToContact, setAgreeToContact] = useState(true);
    const toast = useToast();
    const { isLoggedIn, userEmail } = useAuth();

    useEffect(() =>
    {
        if(isLoggedIn && userEmail)
        {
            setEmail(userEmail);
        }
    }, [isLoggedIn, userEmail]);

    const handleSubmit = async () =>
    {
        if (!email || !feedback)
        {
            toast({
                title: "Error",
                description: "Please fill in both email and feedback fields.",
                status: "error",
                duration: 3000,
                isClosable: true,
            });
            return;
        }

        try
        {
            const response = await fetch(getURL('/send-feedback-email'), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email,
                    text: `${feedback}\n\nAgree to contact: ${agreeToContact ? 'Yes' : 'No'}`,
                }),
            });

            if (response.ok)
            {
                toast({
                    title: "Success",
                    description: "Your feedback has been sent successfully.",
                    status: "success",
                    duration: 3000,
                    isClosable: true,
                });
                onClose();
            }
            else
            {
                throw new Error('Failed to send feedback');
            }
        }
        catch (error)
        {
            toast({
                title: "Error",
                description: "Failed to send feedback. Please try again.",
                status: "error",
                duration: 3000,
                isClosable: true,
            });
        }
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} isCentered>
            <ModalOverlay bg="blackAlpha.300" backdropFilter="blur(10px)" />
            <ModalContent
                bg="rgba(20, 25, 43, 0.95)"
                color="white"
                borderRadius="xl"
                boxShadow="xl"
            >
                <ModalHeader color="orange.400">Send Feedback</ModalHeader>
                <ModalCloseButton />
                <ModalBody>
                    <VStack spacing={4}>
                        <Input
                            placeholder="Your email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            bg="whiteAlpha.200"
                            border="none"
                            _focus={{ bg: "whiteAlpha.300" }}
                            isReadOnly={isLoggedIn}
                        />
                        <Textarea
                            placeholder="Your feedback"
                            value={feedback}
                            onChange={(e) => setFeedback(e.target.value)}
                            bg="whiteAlpha.200"
                            border="none"
                            _focus={{ bg: "whiteAlpha.300" }}
                            rows={5}
                        />
                        <Checkbox
                            isChecked={agreeToContact}
                            onChange={(e) => setAgreeToContact(e.target.checked)}
                            colorScheme="orange"
                        >
                            I agree to be contacted regarding my feedback
                        </Checkbox>
                        <Text fontSize="sm" color="gray.400">
                            Your email is being recorded. By filling this out, you agree to our terms of service and privacy policy.
                        </Text>
                    </VStack>
                </ModalBody>
                <ModalFooter>
                    <Button variant="ghost" mr={3} onClick={onClose} _hover={{ bg: "whiteAlpha.200" }}>
                        Cancel
                    </Button>
                    <Button colorScheme="orange" onClick={handleSubmit}>
                        Send Feedback
                    </Button>
                </ModalFooter>
            </ModalContent>
        </Modal>
    );
};

export default FeedbackModal;