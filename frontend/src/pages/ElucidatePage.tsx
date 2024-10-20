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
  Select,
  Input,
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
} from "@chakra-ui/react";

import Cookies from 'js-cookie';

import { ViewIcon, ViewOffIcon, ChevronDownIcon, ChevronUpIcon, ArrowUpDownIcon } from "@chakra-ui/icons";

// components and custom things
import Turnstile from "../components/Turnstile";
import CopyButton from "../components/CopyButton";
import DownloadButton from "../components/DownloadButton";
import HowToUseSection from "../components/HowToUseSection";
import LegalLinks from "../components/LegalLinks";
import { getURL, encryptWithAccessToken, decryptWithAccessToken } from "../utils";

type FormInput = 
{
  userAPIKey: string,
  llmType: string,
  model: string,
  untranslatedText: string,
  translatedText: string,
  evaluationInstructions: string,
  elucidateCustomInstructionFormat: string,
  instructionPreset: string,
};

type ResponseValues = 
{
  evaluatedText: string;
};

function ElucidatePage() 
{
  useEffect(() => 
  {
    document.title = 'Kakusui | Elucidate';
  }, []);

  const { register, handleSubmit, watch, formState: { isSubmitting, errors }, setValue, getValues } = useForm<FormInput>({
    defaultValues: 
    {
      llmType: "OpenAI",
      model: "gpt-4o-mini",
      instructionPreset: "minimal",
      elucidateCustomInstructionFormat: `You are a professional translation evaluator. Please evaluate the provided translation according to the instructions below. Your response should not contain anything aside from the re-evaluated text.
Untranslated Text:
{{untranslatedText}}
Translated Text:
{{translatedText}}
{{#if evaluationInstructions}}
Evaluation Instructions:
{{evaluationInstructions}}
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
  const access_token = localStorage.getItem('access_token');

  useEffect(() => 
  {
    const warmUpAPI = async () => 
    {
      try 
      {
        await fetch(getURL("/v1/elucidate"), { method: "GET" });
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

  useEffect(() => 
  {
    const savedEvaluationInstructions = localStorage.getItem('elucidate_evaluationInstructions');
    const savedElucidateCustomInstructionFormat = localStorage.getItem('elucidate_customInstructionFormat');
    const savedInstructionPreset = localStorage.getItem('elucidate_instructionPreset');
    
    if (savedEvaluationInstructions) setValue('evaluationInstructions', savedEvaluationInstructions);
    if (savedElucidateCustomInstructionFormat) setValue('elucidateCustomInstructionFormat', savedElucidateCustomInstructionFormat);
    if (savedInstructionPreset) setValue('instructionPreset', savedInstructionPreset);
  }, [setValue]);

  const selectedLLM = watch("llmType");
  const selectedModel = watch("model");
  const selectedInstructionPreset = watch("instructionPreset");

  useEffect(() => 
  {
    const updateModelOptions = () => 
    {
      const options = getModelOptions(selectedLLM);
      setModelOptions(options);
      if (!options.includes(selectedModel)) 
      {
        setValue("model", options[0]);
      }
    };

    const updateApiKey = () => 
    {
      if (!access_token) return;

      const encryptedApiKey = Cookies.get(`elucidate_${selectedLLM.toLowerCase()}_apiKey`);
      if (encryptedApiKey) 
      {
        try 
        {
          const decryptedApiKey = decryptWithAccessToken(encryptedApiKey, access_token);
          setValue("userAPIKey", decryptedApiKey);
        } 
        catch (error) 
        {
          console.error("Failed to decrypt API key:", error);
          Cookies.remove(`elucidate_${selectedLLM.toLowerCase()}_apiKey`);
        }
      } 
      else 
      {
        setValue("userAPIKey", "");
      }
    };

    updateModelOptions();
    updateApiKey();
  }, [selectedLLM, setValue, access_token]);

  useEffect(() => {
    if (selectedInstructionPreset === "minimal") 
    {
      setValue("elucidateCustomInstructionFormat", `You are a professional translation evaluator. Please evaluate the provided translation according to the instructions below. Your response should not contain anything aside from the re-evaluated text.
Untranslated Text:
{{untranslatedText}}
Translated Text:
{{translatedText}}
{{#if evaluationInstructions}}
Evaluation Instructions:
{{evaluationInstructions}}
{{/if}}
      `);
    } 
    else if (selectedInstructionPreset === "verbose") 
    {
      setValue("elucidateCustomInstructionFormat", `You are a professional translation evaluator. Please evaluate the provided translation according to the instructions below. Provide detailed reasoning for any changes and include the re-evaluated text at the end.
Untranslated Text:
{{untranslatedText}}
Translated Text:
{{translatedText}}
{{#if evaluationInstructions}}
Evaluation Instructions:
{{evaluationInstructions}}
{{/if}}
      `);
    }
  }, [selectedInstructionPreset, setValue]);

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
    const requiredPlaceholders = ["{{untranslatedText}}", "{{translatedText}}", "{{evaluationInstructions}}"];
    return requiredPlaceholders.every(placeholder => instructions.includes(placeholder));
  };

  const onSubmit = async (data: FormInput) => 
  {
    setResetTurnstile(false);

    if (window.location.hostname === "kakusui-org.pages.dev") 
    {
      showToast("Access Denied", "This domain is not for end user usage, please use kakusui.org", "error");
      return;
    }

    if (!turnstileToken && window.location.hostname === "kakusui.org") 
    {
      showToast("Verification failed", "Please complete the verification", "error");
      return;
    }

    if (!validateInstructions(data.elucidateCustomInstructionFormat)) 
    {
      showToast("Invalid Instructions", "Instructions must include {{untranslatedText}}, {{translatedText}}, and {{evaluationInstructions}} placeholders.", "error");
      return;
    }

    try {
      if (window.location.hostname === "kakusui.org" && !(await handleVerification())) 
      {
        throw new Error("Turnstile verification failed. Please try again.");
      }

      localStorage.setItem(`elucidate_${data.llmType}_apiKey`, data.userAPIKey);
      localStorage.setItem('elucidate_evaluationInstructions', data.evaluationInstructions);
      localStorage.setItem('elucidate_customInstructionFormat', data.elucidateCustomInstructionFormat);
      localStorage.setItem('elucidate_instructionPreset', data.instructionPreset);

      let evaluationInstructions = data.elucidateCustomInstructionFormat
        .replace("{{untranslatedText}}", data.untranslatedText)
        .replace("{{translatedText}}", data.translatedText)
        .replace("{{evaluationInstructions}}", data.evaluationInstructions);

      if (data.evaluationInstructions) 
      {
        evaluationInstructions = evaluationInstructions.replace("{{#if evaluationInstructions}}\nEvaluation instructions:\n{{evaluationInstructions}}\n{{/if}}", `Evaluation instructions:\n${data.evaluationInstructions}`);
      } 
      else 
      {
        evaluationInstructions = evaluationInstructions.replace("{{#if evaluationInstructions}}\nEvaluation instructions:\n{{evaluationInstructions}}\n{{/if}}", '');
      }

      const textToEvaluate = `Untranslated Text:\n${data.untranslatedText}\n\nTranslated Text:\n${data.translatedText}`;

      const response = await fetch(getURL("/proxy/elucidate"), 
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...data, textToEvaluate, evaluationInstructions }),
      });

      const result = await response.json();
      if (!response.ok) throw new Error(result.message || "An unknown error occurred");

      setResponse(result);

      if (access_token) {
        const encryptedApiKey = encryptWithAccessToken(data.userAPIKey, access_token);
        Cookies.set(`elucidate_${data.llmType.toLowerCase()}_apiKey`, encryptedApiKey, { 
          secure: true,
          sameSite: 'strict'
        });
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

  const handlePaste = async (field: "untranslatedText" | "translatedText") => 
    {
    try 
    {
      const text = await navigator.clipboard.readText();
      setValue(field, text);
    } 
    catch (error) 
    {
      showToast("Error", "Failed to read clipboard contents", "error");
    }
  };

  const handleSwap = () => 
  {
    const currentInput = getValues("untranslatedText");
    const currentOutput = response?.evaluatedText || "";
    setValue("untranslatedText", currentOutput);
    setResponse({ evaluatedText: currentInput });
  };

  const memoizedTurnstile = useMemo(() =>
    // Meant for client side code
    <Turnstile siteKey="0x4AAAAAAAbu-SlGyNF03684" onVerify={setTurnstileToken} resetKey={resetTurnstile} />
    , [resetTurnstile]);

  return (
    <>
      <form onSubmit={handleSubmit(onSubmit)}>
        <VStack spacing={4} align="stretch">
          <FormControl isInvalid={!!errors.untranslatedText}>
            <FormLabel>Untranslated Text</FormLabel>
            <Textarea
              {...register("untranslatedText", { required: true })}
              placeholder="Enter untranslated text"
              rows={5}
            />
            <Button onClick={() => handlePaste("untranslatedText")} mt={2} width="100%">Paste</Button>
          </FormControl>

          <FormControl isInvalid={!!errors.translatedText}>
            <FormLabel>Translated Text</FormLabel>
            <Textarea
              {...register("translatedText", { required: true })}
              placeholder="Enter translated text"
              rows={5}
            />
            <Button onClick={() => handlePaste("translatedText")} mt={2} width="100%">Paste</Button>
          </FormControl>

          <FormControl isInvalid={!!errors.evaluationInstructions}>
            <FormLabel>Evaluation Instructions</FormLabel>
            <Textarea
              {...register("evaluationInstructions", { required: true })}
              placeholder="Enter evaluation instructions"
              rows={4}
            />
          </FormControl>

          <FormControl isInvalid={!!errors.instructionPreset}>
            <FormLabel>Instruction Preset</FormLabel>
            <Select {...register("instructionPreset", { required: true })}>
              <option value="minimal">Minimal</option>
              <option value="verbose">Verbose</option>
              <option value="custom">Custom</option>
            </Select>
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
              <FormControl mt={4} isInvalid={!!errors.elucidateCustomInstructionFormat}>
                <FormLabel>Custom Instruction Format</FormLabel>
                <Textarea
                  {...register("elucidateCustomInstructionFormat", {
                    required: true,
                    validate: validateInstructions
                  })}
                  placeholder="Enter custom instructions with placeholders {{untranslatedText}}, {{translatedText}}, and {{evaluationInstructions}}"
                  rows={6}
                />
                <Text color="red.500" fontSize="sm" mt={2}>
                  {errors.elucidateCustomInstructionFormat && "Instructions must include {{untranslatedText}}, {{translatedText}}, and {{evaluationInstructions}} placeholders."}
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

        {!isBlacklistedDomain && (
          <Center mt={4}>
            {memoizedTurnstile}
          </Center>
        )}

        {response && (
          <>
            <Flex align="center" mt={17} gap={2}>
              <Box flex={1}>
                <Text mb="8px">
                  Evaluated Text
                  <DownloadButton text={response.evaluatedText} fileName="evaluatedText" />
                  <CopyButton text={response.evaluatedText} />
                </Text>
                <Box overflowY="scroll" height={200}>
                  <Text style={{ whiteSpace: "pre-wrap" }}>{response.evaluatedText}</Text>
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
        repositoryUrl="https://github.com/Kakusui/Elucidate"
        steps={[
          "Input the untranslated text.",
          "Input the translated text.",
          "Specify the evaluation instructions.",
          "Select the instruction preset.",
          "Select the LLM and model you want to use.",
          "Provide your API key.",
          "Click 'Submit' to get the evaluated text.",
          "Review the evaluated text and download or copy if necessary.",
          "(For custom format specifiers click the dropdown)"
        ]}
        notes={[
          "Please note that the Turnstile verification is required to use this tool. This is in place to prevent abuse and ensure fair usage. You must complete the verification for every submission.",
          "The Elucidate endpoint access is provided for free here (excluding LLM costs), but please be mindful of the usage and do not abuse the service.",
        ]}
        contactEmail="contact@kakusui.org"
      />

      <LegalLinks basePath="/elucidate" />
    </>
  );
}

export default ElucidatePage;
