/*
Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
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

const ForbiddenPage = () => {
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
            Hmm...
          </Heading>
          <Text fontSize="2xl" fontWeight="semibold">
            403 - Forbidden
          </Text>
          <Text fontSize="lg" color="gray.500">
            We don't think you you're allowed to do that...
          </Text>
          <Button
            as="a"
            href="/"
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

export default ForbiddenPage;