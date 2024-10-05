// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// react
import { useEffect, useMemo, useState } from "react";
import { useForm } from "react-hook-form";

// chakra-ui
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
  Collapse,
  Radio,
  RadioGroup
} from "@chakra-ui/react";

import { ViewIcon, ViewOffIcon, ChevronDownIcon, ChevronUpIcon, ArrowUpDownIcon } from "@chakra-ui/icons";

// components and custom things
import Turnstile from "../components/Turnstile";
import CopyButton from "../components/CopyButton";
import DownloadButton from "../components/DownloadButton";
import HowToUseSection from "../components/HowToUseSection";
import LegalLinks from "../components/LegalLinks";
import { getURL } from "../utils";
import { useAuth } from "../contexts/AuthContext";

type FormInput = 
{
  userAPIKey: string,
  llmType: string,
  model: string,
  textToTranslate: string,
  language: string,
  tone: string,
  additional_instructions: string,
  easytlCustomInstructionFormat: string,
  paymentMethod: string,
};

type ResponseValues = 
{
  translatedText: string;
  credits?: number;
};

function EasyTLPage()  
{
  useEffect(() => {
    document.title = 'Kakusui | EasyTL';
  }, []);

  const { register, handleSubmit, watch, formState: { isSubmitting, errors }, setValue, getValues } = useForm<FormInput>({
    defaultValues: 
    {
      tone: "Formal; Polite",
      llmType: "OpenAI",
      model: "gpt-4o-mini",
      paymentMethod: "credits",
      easytlCustomInstructionFormat: `You are a professional translator, please translate the text given to you following the below instructions. Do not use quotations or say anything else aside from the translation in your response.
Language: {{language}}
Tone: {{tone}}
{{#if additional_instructions}}
Additional instructions:
{{additional_instructions}}
{{/if}}
      `
    }
  });

  const [showApiKey, setShowApiKey] = useState(false);
  const [turnstileToken, setTurnstileToken] = useState<string | null>(null);
  const [isBlacklistedDomain, setBlacklistedDomain] = useState(false);
  const [resetTurnstile, setResetTurnstile] = useState(false);
  const [response, setResponse] = useState<ResponseValues | null>(null);
  const [modelOptions, setModelOptions] = useState<string[]>([]);
  const [isAdvancedSettingsVisible, setAdvancedSettingsVisible] = useState(false);
  const toast = useToast();
  const { isPrivilegedUser, credits, updateCredits, isLoggedIn } = useAuth();

  const access_token = localStorage.getItem('access_token');

  const selectedLLM = watch("llmType");
  const selectedModel = watch("model");
  const selectedPaymentMethod = watch("paymentMethod");

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
        // ignore
      }
    };
    warmUpAPI();
  }, []);

  useEffect(() => 
  {
    const currentDomain = window.location.hostname;
    setBlacklistedDomain(currentDomain !== "kakusui.org");
  }, []);

  useEffect(() => {
    const savedTone = localStorage.getItem('easytl_tone');
    const savedLanguage = localStorage.getItem('easytl_language');
    const savedAdditionalInstructions = localStorage.getItem('easytl_additional_instructions');
    const savedEasytlCustomInstructionFormat = localStorage.getItem('easytl_custom_instruction_format');
    
    if (savedTone) setValue('tone', savedTone);
    if (savedLanguage) setValue('language', savedLanguage);
    if (savedEasytlCustomInstructionFormat) setValue('easytlCustomInstructionFormat', savedEasytlCustomInstructionFormat);
    if (savedAdditionalInstructions) setValue('additional_instructions', savedAdditionalInstructions);
  }, [setValue]);

  useEffect(() => {
    const updateModelOptions = () => {
      const options = getModelOptions(selectedLLM);
      setModelOptions(options);
      if (!options.includes(selectedModel)) {
        setValue("model", options[0]);
      }
    };

    const updateApiKey = () => {
      const savedApiKey = localStorage.getItem(`easytl_${selectedLLM.toLowerCase()}_apiKey`);
      setValue("userAPIKey", savedApiKey || "");
    };

    updateModelOptions();
    updateApiKey();
  }, [selectedLLM, setValue, selectedModel]);

  const handleToggleShowApiKey = () => setShowApiKey(!showApiKey);

  const getModelOptions = (llm: string): string[] => 
  {
    switch (llm) 
    {
      case "OpenAI":
        return ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-4o", "gpt-4o-mini"]
      case "Gemini":
        return ["gemini-1.0-pro", "gemini-1.5-pro", "gemini-1.5-flash"];
      case "Anthropic":
        return ["claude-3-haiku-20240307", "claude-3-sonnet-20240229", "claude-3-opus-20240229", "claude-3-5-sonnet-20240620"]
      default:
        return [];
    }
  };

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
      const verificationResponse = await fetch(getURL("/auth/verify-turnstile"), 
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

  const validateInstructions = (instructions: string) => 
  {
    const requiredPlaceholders = ["{{language}}", "{{tone}}"];
    return requiredPlaceholders.every(placeholder => instructions.includes(placeholder));
  };

  const calculateTokenCost = async (data: FormInput) => 
  {
    try 
    {
      let translationInstructions = data.easytlCustomInstructionFormat
        .replace("{{language}}", data.language)
        .replace("{{tone}}", data.tone);

      if (data.additional_instructions) 
      {
        translationInstructions = translationInstructions.replace("{{#if additional_instructions}}\nAdditional instructions:\n{{additional_instructions}}\n{{/if}}", `Additional instructions:\n${data.additional_instructions}`);
      } 
      else 
      {
        translationInstructions = translationInstructions.replace("{{#if additional_instructions}}\nAdditional instructions:\n{{additional_instructions}}\n{{/if}}", '');
      }

      const response = await fetch(getURL("/proxy/calculate-token-cost"), 
      {
        method: "POST",
        headers: 
        { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${access_token}` 
        },
        body: JSON.stringify({
          text_to_translate: data.textToTranslate,
          translation_instructions: translationInstructions,
          model: data.model
        }),
      });

      if (!response.ok) 
      {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      return result.cost;
    } 
    catch (error) 
    {
      console.error("Error calculating token cost:", error);
      showToast("Error", "Failed to calculate token cost", "error");
      return null;
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

    if(selectedPaymentMethod !== "credits" && window.location.hostname === "kakusui.org" && !turnstileToken)
    {
      showToast("Verification failed", "Please complete the verification", "error");
      return;
    }

    if (!validateInstructions(data.easytlCustomInstructionFormat)) 
    {
      showToast("Invalid Instructions", "Instructions must include {{language}} and {{tone}} placeholders.", "error");
      return;
    }

    try 
    {
      if(window.location.hostname === "kakusui.org" && selectedPaymentMethod !== "credits" && !(await handleVerification()))
      {
        throw new Error("Turnstile verification failed. Please try again.");
      }

      const estimatedCost = await calculateTokenCost(data);
      
      if (data.paymentMethod === "credits") 
      {
        if (!isLoggedIn) 
        {
          showToast("Authentication Required", "Please log in to use credits for translation.", "error");
          return;
        }
        
        if (estimatedCost && estimatedCost > credits) 
        {
          showToast("Insufficient Credits", "You don't have enough credits for this translation.", "error");
          return;
        }
      }

      localStorage.setItem(`easytl_${data.llmType.toLowerCase()}_apiKey`, data.userAPIKey);
      localStorage.setItem('easytl_tone', data.tone);
      localStorage.setItem('easytl_language', data.language);
      localStorage.setItem('easytl_additional_instructions', data.additional_instructions);
      localStorage.setItem('easytl_custom_instruction_format', data.easytlCustomInstructionFormat);

      let translationInstructions = data.easytlCustomInstructionFormat
        .replace("{{language}}", data.language)
        .replace("{{tone}}", data.tone);

      if (data.additional_instructions) 
      {
        translationInstructions = translationInstructions.replace("{{#if additional_instructions}}\nAdditional instructions:\n{{additional_instructions}}\n{{/if}}", `Additional instructions:\n${data.additional_instructions}`);
      } 
      else 
      {
        translationInstructions = translationInstructions.replace("{{#if additional_instructions}}\nAdditional instructions:\n{{additional_instructions}}\n{{/if}}", '');
      }

      const requestBody = {
        textToTranslate: data.textToTranslate,
        translationInstructions,
        llmType: data.llmType.toLowerCase(),
        userAPIKey: isPrivilegedUser || data.paymentMethod === "credits" ? "" : data.userAPIKey,
        model: data.model,
        using_credits: data.paymentMethod === "credits"
      };

      const response = await fetch(getURL("/proxy/easytl"), 
      {
        method: "POST",
        headers: 
        { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${access_token}` 
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) 
      {
        const errorText = await response.text();
        console.error(`Error response: ${response.status} ${response.statusText}`);
        console.error(`Error details: ${errorText}`);
        throw new Error(`HTTP error! status: ${response.status} ${errorText}`);
      }

      const result = await response.json();
      setResponse(result);

      if (data.paymentMethod === "credits") 
      {
        updateCredits(result.credits);
      }
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

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      setValue("textToTranslate", text);
    } catch (error) {
      showToast("Error", "Failed to read clipboard contents", "error");
    }
  };

  const handleSwap = () => {
    const currentInput = getValues("textToTranslate");
    const currentOutput = response?.translatedText || "";
    setValue("textToTranslate", currentOutput);
    setResponse({ translatedText: currentInput });
  };

  const memoizedTurnstile = useMemo(() =>
    <Turnstile siteKey="0x4AAAAAAAbu-SlGyNF03684" onVerify={setTurnstileToken} resetKey={resetTurnstile} />
  , [resetTurnstile]);

  return (
    <>
      <form onSubmit={handleSubmit(onSubmit)}>
        <VStack spacing={4} align="stretch">
          <FormControl isInvalid={!!errors.language}>
            <FormLabel>Language</FormLabel>
            <Input {...register("language", { required: true })} placeholder="Enter language" />
          </FormControl>

          <FormControl isInvalid={!!errors.textToTranslate}>
            <FormLabel>Text to Translate</FormLabel>
            <Textarea 
              {...register("textToTranslate", { required: true })} 
              placeholder="Enter text to translate" 
              rows={5} 
            />
            <Button onClick={handlePaste} mt={2} width="100%">Paste</Button>
          </FormControl>

          <FormControl isInvalid={!!errors.tone}>
            <FormLabel>Tone</FormLabel>
            <Textarea {...register("tone", { required: true })} placeholder="Enter tone (use semicolons for separators; words/phrases only)" rows={2} />
          </FormControl>

          <FormControl isInvalid={!!errors.additional_instructions}>
            <FormLabel>Additional Instructions</FormLabel>
            <Textarea
              {...register("additional_instructions")} 
              placeholder="Enter any additional instructions (optional)"
              rows={4}
            />
          </FormControl>

          <HStack spacing={4} align="flex-start">
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

            {(selectedPaymentMethod === "api_key") && (
              <FormControl isInvalid={!!errors.userAPIKey} flex={1}>
                <FormLabel>API Key</FormLabel>
                <InputGroup>
                  <Input
                    {...register("userAPIKey", { required: selectedPaymentMethod === "api_key" })}
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
            )}
          </HStack>

          <FormControl as="fieldset">
            <FormLabel as="legend">Payment Method</FormLabel>
            <RadioGroup defaultValue="credits">
              <HStack spacing="24px">
                <Radio {...register("paymentMethod")} value="credits">Credits</Radio>
                <Radio {...register("paymentMethod")} value="api_key">API Key</Radio>
              </HStack>
            </RadioGroup>
          </FormControl>

          <Box width="100%">
            <Button 
              mt={4} 
              width="100%" 
              variant="outline" 
              leftIcon={isAdvancedSettingsVisible ? <ChevronUpIcon /> : <ChevronDownIcon />}
              onClick={() => setAdvancedSettingsVisible(!isAdvancedSettingsVisible)}
            >
              Advanced Settings
            </Button>
            <Collapse in={isAdvancedSettingsVisible} animateOpacity>
              <FormControl mt={4} isInvalid={!!errors.easytlCustomInstructionFormat}>
                <FormLabel>Custom Instruction Format</FormLabel>
                <Textarea
                  {...register("easytlCustomInstructionFormat", { 
                    required: true, 
                    validate: validateInstructions 
                  })} 
                  placeholder="Enter custom instructions with placeholders {{language}} and {{tone}}"
                  rows={6}
                />
                <Text color="red.500" fontSize="sm" mt={2}>
                  {errors.easytlCustomInstructionFormat && "Instructions must include {{language}} and {{tone}} placeholders."}
                </Text>
              </FormControl>
            </Collapse>
          </Box>

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

        {selectedPaymentMethod !== "credits" && !isBlacklistedDomain && (
          <Center mt={4}>
            {memoizedTurnstile}
          </Center>
        )}

        {response && (
          <>
            <Flex align="center" mt={17} gap={2}>
              <Box flex={1}>
                <Text mb="8px">
                  Translated Text
                  <DownloadButton text={response.translatedText} fileName="translatedText" />
                  <CopyButton text={response.translatedText} />
                </Text>
                <Box overflowY="scroll" height={200}>
                  <Text style={{ whiteSpace: "pre-wrap" }}>{response.translatedText}</Text>
                </Box>
              </Box>
              <IconButton onClick={handleSwap} variant="ghost" size="xl" aria-label="Swap text" icon={<ArrowUpDownIcon />} />
            </Flex>
            <Center>
              <Button onClick={() => setResponse(null)} mb={17} colorScheme="orange" variant="ghost">Clear Logs</Button>
            </Center>
          </>
        )}
      </form>

      <HowToUseSection
        repositoryUrl="https://github.com/Bikatr7/EasyTL"
        steps={[
          "Input the text you want to translate.",
          "Specify the language and tone for the translation.",
          "Include optional additional instructions.",
          "Select the LLM and model you want to use.",
          "Choose your payment method (Credits or API Key).",
          "If using API Key, provide your API key.",
          "Click 'Submit' to get the translated text.",
          "Review the translated text and download or copy if necessary.",
          "(For custom format specifiers click the dropdown)"
        ]}
        notes={[
          "Please note that the Turnstile verification is required to use this tool. This is in place to prevent abuse and ensure fair usage. You must complete the verification for every submission.",
          "The EasyTL endpoint access is provided for free here (excluding LLM costs), but please be mindful of the usage and do not abuse the service."
        ]}
        contactEmail="contact@kakusui.org"
      />

      <LegalLinks basePath="/easytl" />
    </>
  );
}

export default EasyTLPage;