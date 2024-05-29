/*
Copyright Kakusui LLC 2024 (https://kakusui.org) (https://github.com/Kakusui)
Use of this source code is governed by a GNU General Public License v3.0
license that can be found in the LICENSE file.
*/

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
      bg="gray.800"
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
          <Text fontSize="lg">
            It seems like either we can't code or you went to a page that doesn't exist...
          </Text>
          <Button
            as="a"
            href="/"
            bg="blue.600"
            color="white"
            py={2}
            px={4}
            rounded="md"
            mb={4}
            _hover={{
              bg: "black",
              color: "blue.600",
              transition: "0.3s",
            }}
          >
            Return to Home
          </Button>
          <chakra.a
            href="https://github.com/kakusui/kakusui-org/issues"
            target="_blank"
            color="blue.400"
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