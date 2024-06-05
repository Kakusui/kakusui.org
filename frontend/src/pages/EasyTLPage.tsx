/*
Copyright Kakusui LLC 2024 (https://kakusui.org) (https://github.com/Kakusui)
Use of this source code is governed by a GNU Lesser General Public License v2.1
license that can be found in the LICENSE file.
*/

import { useEffect, useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import {
  Button,
  FormControl,
  FormLabel,
  Input,
  Select,
  Textarea,
  VStack,
  HStack,
  InputGroup,
  InputRightElement,
  IconButton,
  useToast,
  Center,
  Box,
  Flex,
  Text,
} from "@chakra-ui/react";

import { ViewIcon, ViewOffIcon, DownloadIcon } from "@chakra-ui/icons";

import Turnstile from "../components/Turnstile";
import { getURL } from "../utils";

type FormInput = 
{
  userAPIKey: string,
  llmType: string,
  model: string,
  textToTranslate: string,
  language: string,
  tone: string,
};

type ResponseValues = 
{
  translatedText: string;
};

function EasyTLPage() 
{
  const { register, handleSubmit, watch, formState: { isSubmitting, errors } } = useForm<FormInput>({
    defaultValues: {
      tone: "Formal Polite",
      llmType: "OpenAI",
      model: "gpt-3.5-turbo",
    }
  });

  const [showApiKey, setShowApiKey] = useState(false);
  const [turnstileToken, setTurnstileToken] = useState<string | null>(null);
  const [isBlacklistedDomain, setBlacklistedDomain] = useState(false);
  const [resetTurnstile, setResetTurnstile] = useState(false);
  const [response, setResponse] = useState<ResponseValues | null>(null);
  const toast = useToast();

  useEffect(() => 
  {
    const warmUpAPI = async () => 
    {
      try
      {
        await fetch(getURL("/v1/easytl"), { method: "GET" });
      } 
      catch 
      {
        // handle error silently
      }
    };
    warmUpAPI();
  }, []);

  useEffect(() => 
  {
    const currentDomain = window.location.hostname;
    setBlacklistedDomain(currentDomain !== "kakusui.org");
  }, []);

  const handleToggleShowApiKey = () => setShowApiKey(!showApiKey);

  const selectedLLM = watch("llmType");

  const getModelOptions = (llm: string): string[] => 
  {
    switch (llm) 
    {
      case "OpenAI":
        return ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-4o"];
      case "Gemini":
        return ["gemini-1.0-pro", "gemini-1.5-pro"];
      case "Anthropic":
        return ["claude-3-haiku-20240307", "claude-3-sonnet-20240229", "claude-3-opus-20240229"];
      default:
        return [];
    }
  };

  const modelOptions = getModelOptions(selectedLLM);

  const showToast = (title: string, description: string, status: "success" | "error") => 
  {
    toast({
      title,
      description,
      status,
      duration: 5000,
      isClosable: true,
    });
  };

  const handleVerification = async () => 
  {
    try 
    {
      const verificationResponse = await fetch(getURL("/verify-turnstile"), 
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: turnstileToken }),
      });

      const verificationResult = await verificationResponse.json();
      return verificationResult.success;
    } 
    catch 
    {
      return false;
    }
  };

  const onSubmit = async (data: FormInput) => 
  {
    setResetTurnstile(false);

    if(window.location.hostname === "kakusui-org.pages.dev")
    {
      showToast("Access Denied", "This domain is not for end user usage, please use kakusui.org", "error");
      return;
    }

    if(!turnstileToken && window.location.hostname === "kakusui.org")
    {
      showToast("Verification failed", "Please complete the verification", "error");
      return;
    }

    try 
    {
      if(window.location.hostname === "kakusui.org" && !(await handleVerification()))
      {
        throw new Error("Turnstile verification failed");
      }

      const translationInstructions = `Translate to ${data.language} with a ${data.tone} tone.`;

      const response = await fetch(getURL("/proxy/easytl"), 
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...data, translationInstructions }),
      });

      const result = await response.json();
      if(!response.ok) throw new Error(result.message || "An unknown error occurred");

      setResponse(result);
    } 
    catch (error) 
    {
      console.error("Error Occurred:", error);
      showToast("An error occurred.", (error as Error).message || "An error occurred.", "error");
    } 
    finally 
    {
      setResetTurnstile(true);
    }
  };

  const downloadOutput = (input: 'translatedText') => 
  {
    const content = response?.translatedText;
    if(!content) return;

    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.download = `${input}.txt`;
    link.href = url;
    link.click();
  };

  const memoizedTurnstile = useMemo(() =>
    <Turnstile siteKey="0x4AAAAAAAbu-SlGyNF03684" onVerify={setTurnstileToken} resetKey={resetTurnstile} />
  , [resetTurnstile]);

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <VStack spacing={4} align="stretch">
        <FormControl isInvalid={!!errors.language}>
          <FormLabel>Language</FormLabel>
          <Input {...register("language", { required: true })} placeholder="Enter language" />
        </FormControl>

        <FormControl isInvalid={!!errors.textToTranslate}>
          <FormLabel>Text to Translate</FormLabel>
          <Textarea {...register("textToTranslate", { required: true })} placeholder="Enter text to translate" rows={5} />
        </FormControl>

        <FormControl isInvalid={!!errors.tone}>
          <FormLabel>Tone</FormLabel>
          <Textarea {...register("tone", { required: true })} placeholder="Enter tone" rows={2} />
        </FormControl>

        <HStack spacing={4}>
          <FormControl isInvalid={!!errors.llmType} flex={1}>
            <FormLabel>LLM</FormLabel>
            <Select {...register("llmType", { required: true })}>
              <option value="OpenAI">OpenAI</option>
              <option value="Gemini">Gemini</option>
              <option value="Anthropic">Anthropic</option>
            </Select>
          </FormControl>

          <FormControl isInvalid={!!errors.model} flex={1}>
            <FormLabel>Model</FormLabel>
            <Select {...register("model", { required: true })}>
              {modelOptions.map((model) => (
                <option key={model} value={model}>{model}</option>
              ))}
            </Select>
          </FormControl>

          <FormControl isInvalid={!!errors.userAPIKey} flex={1}>
            <FormLabel>API Key</FormLabel>
            <InputGroup>
              <Input
                {...register("userAPIKey", { required: true })}
                type={showApiKey ? "text" : "password"}
                placeholder="Enter API key"
              />
              <InputRightElement>
                <IconButton
                  aria-label={showApiKey ? "Hide API key" : "Show API key"}
                  icon={showApiKey ? <ViewOffIcon /> : <ViewIcon />}
                  onClick={handleToggleShowApiKey}
                  variant="ghost"
                />
              </InputRightElement>
            </InputGroup>
          </FormControl>
        </HStack>

        <Button
          mt={4}
          width="100%"
          type="submit"
          bg="orange.400"
          color="white"
          _hover={{ bg: 'orange.500' }}
          isLoading={isSubmitting}
        >
          Submit
        </Button>
      </VStack>

      {!isBlacklistedDomain && (
        <Center mt={4}>
          {memoizedTurnstile}
        </Center>
      )}

      {response && (
        <>
          <Flex mt={17} gap={2}>
            <Box flex={1}>
              <Text mb="8px">
                Translated Text
                <IconButton onClick={() => downloadOutput("translatedText")} variant="ghost" size="xl" aria-label="Download translated text" icon={<DownloadIcon />} />
              </Text>
              <Box overflowY="scroll" height={200}>
                <Text style={{ whiteSpace: "pre-wrap" }}>{response.translatedText}</Text>
              </Box>
            </Box>
          </Flex>
          <Center>
            <Button onClick={() => setResponse(null)} mb={17} colorScheme="orange" variant="ghost">Clear Logs</Button>
          </Center>
        </>
      )}
    </form>
  );
}

export default EasyTLPage;