/*
Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
Use of this source code is governed by a GNU General Public License v3.0
license that can be found in the LICENSE file.
*/

// react things
import React, { useEffect, useMemo, useState, useRef } from "react";
import { useForm } from "react-hook-form";

// custom things
import { getURL } from "../utils";
import Turnstile from "../components/Turnstile";

// chakra things
import {
    Box, Button, Flex, FormErrorMessage, FormControl, FormLabel, IconButton, Text, Textarea, useToast, Center
} from "@chakra-ui/react";
import { ArrowUpIcon } from "@chakra-ui/icons";

import CopyButton from "../components/CopyButton";
import DownloadButton from "../components/DownloadButton";
import HowToUseSection from "../components/HowToUseSection";
import LegalLinks from "../components/LegalLinks";

type FormInput = 
{
    textToPreprocess: string;
    replacementsJson: string;
};

type ResponseValues = 
{
    errorLog: string;
    preprocessedText: string;
    preprocessingLog: string;
};

function KairyouPage() 
{

    useEffect(() => {
        document.title = 'Kakusui | Kairyou';

    }, []);

    const textRef = useRef<HTMLInputElement>(null);
    const jsonRef = useRef<HTMLInputElement>(null);
    const [turnstileToken, setTurnstileToken] = useState<string | null>(null);
    const [isBlacklistedDomain, setBlacklistedDomain] = useState(false);
    const [resetTurnstile, setResetTurnstile] = useState(false);
    const { register, handleSubmit, setValue, formState: { isSubmitting, errors } } = useForm<FormInput>();
    const [response, setResponse] = useState<ResponseValues>();
    const toast = useToast();

    useEffect(() => 
    {
        const warmUpAPI = async () => 
        {
            try
            {
                await fetch(getURL("/v1/kairyou"), { method: "GET" });
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

    const onTurnstileVerify = (token: string) => 
    {
        setTurnstileToken(token);
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

    const validateJSON = (json: string) => 
    {
        try
        {
            JSON.parse(json);
            return true;
        }
        catch
        {
            return false;
        }
    };

    const handleVerification = async () => 
    {
        const verificationResponse = await fetch(getURL("/verify-turnstile"), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: turnstileToken }),
        });

        const verificationResult = await verificationResponse.json();
        return verificationResult.success;
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

        if(!validateJSON(data.replacementsJson))
        {
            showToast("Invalid JSON", "Please provide a valid JSON format.", "error");
            return;
        }

        try
        {
            if(window.location.hostname === "kakusui.org" && !(await handleVerification()))
            {
                throw new Error("Turnstile verification failed");
            }

            const response = await fetch(getURL("/proxy/kairyou"), {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data),
            });

            const result = await response.json();
            if(!response.ok) throw new Error(result.message || "An unknown error occurred");

            setResponse(result);
        }
        catch(error)
        {
            console.error("Error Occurred:", error);
            showToast("An error occurred.", (error as Error).message || "An error occurred.", "error");
        }
        finally
        {
            setResetTurnstile(true);
        }
    };

    const onUpload = async (event: React.ChangeEvent<HTMLInputElement>) => 
    {
        const file = event.target.files?.[0];
        if(!file) return;

        const input = await file.text();
        const fileTypeHandlers: { [key: string]: (input: string) => void } = {
            "text/plain": (input) => setValue("textToPreprocess", input),
            "application/json": (input) => setValue("replacementsJson", input),
        };

        fileTypeHandlers[file.type]?.(input);
    };

    const memoizedTurnstile = useMemo(() => 
    (
        <Turnstile siteKey="0x4AAAAAAAbu-SlGyNF03684" onVerify={onTurnstileVerify} resetKey={resetTurnstile} />
    ), [resetTurnstile]);

    return (
        <>
            <input onChange={onUpload} ref={textRef} type="file" accept=".txt" hidden />
            <input onChange={onUpload} ref={jsonRef} type="file" accept=".json" hidden />
            <form onSubmit={handleSubmit(onSubmit)}>
                <Flex flex={1} gap={2}>
                    <FormControl isInvalid={!!errors.textToPreprocess} flex={1}>
                        <FormLabel>
                            Text Input
                            <IconButton variant="ghost" size="xl" onClick={() => textRef.current?.click()} aria-label="Upload Text" icon={<ArrowUpIcon />} />
                        </FormLabel>
                        <Textarea rows={20} size="sm" {...register("textToPreprocess", { required: true })} />
                        <FormErrorMessage>{errors.textToPreprocess && "Text Input is required"}</FormErrorMessage>
                    </FormControl>
                    <FormControl isInvalid={!!errors.replacementsJson} flex={1}>
                        <FormLabel>
                            JSON Input
                            <IconButton variant="ghost" size="xl" onClick={() => jsonRef.current?.click()} aria-label="Upload JSON" icon={<ArrowUpIcon />} />
                        </FormLabel>
                        <Textarea rows={20} size="sm" {...register("replacementsJson", { required: true })} />
                        <FormErrorMessage>{errors.replacementsJson && "JSON Input is required"}</FormErrorMessage>
                    </FormControl>
                </Flex>

                <Button
                    mb={4} mt={4} width="100%" type="submit"
                    bg="orange.400" color="white"
                    _hover={{ bg: "orange.500" }}
                    isLoading={isSubmitting}
                >
                    Submit
                </Button>
            </form>

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
                                Preprocessing Log
                                <DownloadButton text={response.preprocessingLog} fileName="preprocessing_log" />
                                <CopyButton text={response.preprocessingLog} />
                            </Text>
                            <Box overflowY="scroll" height={200}>
                                <Text style={{ whiteSpace: "pre-wrap" }}>{response.preprocessingLog}</Text>
                            </Box>
                        </Box>
                        {response.errorLog ? (
                            <Box flex={1}>
                                <Text mb="8px">Error Log</Text>
                                <Box overflowY="scroll" height={200}>
                                    <Text style={{ whiteSpace: "pre-wrap" }}>{response.errorLog}</Text>
                                </Box>
                            </Box>
                        ) : (
                            <Box flex={1}>
                                <Text mb="8px">
                                    Output
                                    <DownloadButton text={response.preprocessedText} fileName="preprocessedText" />
                                    <CopyButton text={response.preprocessedText} />
                                </Text>
                                <Box overflowY="scroll" height={200}>
                                    <Text style={{ whiteSpace: "pre-wrap" }}>{response.preprocessedText}</Text>
                                </Box>
                            </Box>
                        )}
                    </Flex>
                    <Center>
                        <Button onClick={() => setResponse(undefined)} mb={17} colorScheme="orange" variant="ghost">Clear Logs</Button>
                    </Center>
                </>
            )}

            <HowToUseSection
                repositoryUrl="https://github.com/Bikatr7/Kairyou"
                steps={[
                    "Upload or input the text you want to preprocess.",
                    "Upload or input the JSON file with replacement rules.",
                    "Click 'Submit' to preprocess the text.",
                    "Review the preprocessing log and output, and download if necessary.",
                    "If there are any errors, they will be displayed in the error log."
                ]}
                notes={[
                    "Please note that the Turnstile verification is required to use this tool. This is in place to prevent abuse and ensure fair usage. You must complete the verification for every submission.",
                    "The Kairyou endpoint access is provided for free here, but please be mindful of the usage and do not abuse the service."
                ]}
                contactEmail="contact@kakusui.org"
            />

            <LegalLinks basePath="/kairyou" />
        </>
    );
}

export default KairyouPage;