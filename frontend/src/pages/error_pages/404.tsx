// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// react
import { useState, useEffect, useRef } from "react";

// chakra-ui
import {
  Button,
  chakra,
  Container,
  Flex,
  Heading,
  Text,
  VStack,
  Box,
  keyframes,
  Code
} from "@chakra-ui/react";

const rotateAnimation = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`;

const launchAnimation = keyframes`
  0% {
    transform: translateY(0) rotate(0deg);
    opacity: 1;
  }
  70% {
    transform: translateY(-200px) rotate(1440deg);
    opacity: 1;
  }
  100% {
    transform: translateY(-300px) rotate(2160deg);
    opacity: 0;
  }
`;

const NotFoundPage = () =>
{
  const [launch, setLaunch] = useState(false);
  const hoverTimer = useRef<NodeJS.Timeout | null>(null);
  const isLaunching = useRef(false);

  const handleMouseEnter = () =>
  {
    if (isLaunching.current) return;

    // Start a timer for 3 seconds before launching
    hoverTimer.current = setTimeout(() =>
    {
      isLaunching.current = true;
      setLaunch(true);
    }, 3000);
  };

  const handleMouseLeave = () =>
  {
    if (hoverTimer.current)
    {
      clearTimeout(hoverTimer.current);
      hoverTimer.current = null;
    }
  };

  const handleAnimationEnd = () =>
  {
    if (launch)
    {
      // Reset the launch state after animation completes
      setLaunch(false);
      isLaunching.current = false;
    }
  };

  // Cleanup timer on unmount
  useEffect(() =>
  {
    return () =>
    {
      if (hoverTimer.current)
      {
        clearTimeout(hoverTimer.current);
      }
    };
  }, []);

  return (
    <Flex
      bg="#14192b"
      minH="87vh"
      align="center"
      justify="center"
      color="white"
      position="relative"
      overflow="hidden"
    >
      <Container textAlign="center" maxW="md" position="relative">
        <VStack spacing={6}>
          <Box
            fontSize="8xl"
            mb={4}
            animation={
              launch
                ? `${launchAnimation} 1.5s forwards`
                : `${rotateAnimation} var(--rotation-duration, 10s) linear infinite`
            }
            sx={{
              "--rotation-duration": "10s",
              "&:hover": {
                "--rotation-duration": "5s",
              },
            }}
            transition="--rotation-duration 2s ease-in-out"
            cursor="pointer"
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
            onAnimationEnd={handleAnimationEnd}
          >
            🌐
          </Box>
          <Heading as="h1" size="2xl">
            Lost in Translation
          </Heading>
          <Text fontSize="xl" color="orange.400">
            404 - Page not found
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
            Return to Safety
          </Button>
          <chakra.a
            href="https://github.com/kakusui/kakusui-org/issues"
            target="_blank"
            color="orange.400"
            _hover={{ color: "white" }}
          >
            Get Our Programmers in Trouble
          </chakra.a>
        </VStack>
      </Container>
    </Flex>
  );
};

export default NotFoundPage;