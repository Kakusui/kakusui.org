/*
Copyright Kakusui LLC 2024 (https://kakusui.org) (https://github.com/Kakusui)
Use of this source code is governed by a GNU Lesser General Public License v2.1
license that can be found in the LICENSE file.
*/

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
} from "@chakra-ui/react";

import { ViewIcon, ViewOffIcon } from "@chakra-ui/icons";

import { useState } from "react";

type FormInput = {
  apiKey: string,
  llm: string,
  model: string,
  language: string,
  textToTranslate: string,
  tone: string,
};

function EasyTLPage() {
  const { register, handleSubmit, watch, formState: { isSubmitting, errors } } = useForm<FormInput>({
    defaultValues: {
      tone: "Formal Polite",
      llm: "OpenAI",
      model: "Dummy openai 1"
    }
  });

  const [showApiKey, setShowApiKey] = useState(false);
  const handleToggleShowApiKey = () => setShowApiKey(!showApiKey);

  const selectedLLM = watch("llm");

  const getModelOptions = (llm: string): string[] => {
switch (llm) {
      case "OpenAI":
        return ["Dummy openai 1", "Dummy openai 2"];
      case "Gemini":
        return ["Dummy gemini 1", "Dummy gemini 2"];
      case "Anthropic":
        return ["Dummy anthropic 1", "Dummy anthropic 2"];
      default:
        return [];
}
  };

  const modelOptions = getModelOptions(selectedLLM);

  const onSubmit = (data: FormInput) => {
    console.log(data);
  };

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
          <Textarea {...register("tone", { required: true })} placeholder="Enter tone" rows={2}/>
        </FormControl>

        <HStack spacing={4}>
          <FormControl isInvalid={!!errors.llm} flex={1}>
            <FormLabel>LLM</FormLabel>
            <Select {...register("llm", { required: true })}>
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

          <FormControl isInvalid={!!errors.apiKey} flex={1}>
            <FormLabel>API Key</FormLabel>
            <InputGroup>
              <Input
                {...register("apiKey", { required: true })}
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
          _hover={{
            bg: 'orange.500',
          }}
          isLoading={isSubmitting}
        >
          Submit
        </Button>
      </VStack>
    </form>
  );
}

export default EasyTLPage;