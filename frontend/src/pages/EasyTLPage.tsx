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
  language: string,
  textToTranslate: string,
  tone: string,
};

function EasyTLPage() {
  const { register, handleSubmit, formState: { isSubmitting, errors } } = useForm<FormInput>({
    defaultValues: {
      tone: "Formal Polite",
    }
  });

  const [showApiKey, setShowApiKey] = useState(false);
  const handleToggleShowApiKey = () => setShowApiKey(!showApiKey);

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
          <Textarea {...register("textToTranslate", { required: true })} placeholder="Enter text to translate" />
        </FormControl>

        <FormControl isInvalid={!!errors.tone}>
          <FormLabel>Tone</FormLabel>
          <Textarea {...register("tone", { required: true })} placeholder="Enter tone" size="sm" />
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