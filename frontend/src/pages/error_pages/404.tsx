// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// chakra-ui
import {
  Button,
  chakra,
  Container,
  Flex,
  Heading,
  Text,
  VStack
} from "@chakra-ui/react";

const NotFoundPage = () => {
  return (
    <Flex
      bg="#14192b"
      minH="87vh"
      align="center"
      justify="center"
      color="white"
    >
      <Container textAlign="center" maxW="md">
        <VStack spacing={6}>
          <Heading as="h1" size="2xl">
            Oops!
          </Heading>
          <Text fontSize="2xl" fontWeight="semibold">
            404 - Page not found
          </Text>
          <Text fontSize="lg" color="gray.500">
            It seems like either we can't code or you went to a page that doesn't exist...
          </Text>
          <Button
            as="a"
            href="/home"
            bg="orange.400"
            color="white"
            py={2}
            px={4}
            rounded="md"
            mb={4}
            _hover={{
              bg: "orange.500",
            }}
          >
            Return to Home
          </Button>
          <chakra.a
            href="https://github.com/kakusui/kakusui-org/issues"
            target="_blank"
            color="orange.400"
            _hover={{ color: "white" }}
          >
            Something Broken? Tell us!
          </chakra.a>
        </VStack>
      </Container>
    </Flex>
  );
};

export default NotFoundPage;