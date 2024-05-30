/*
Copyright Kakusui LLC 2024 (https://kakusui.org) (https://github.com/Kakusui)
Use of this source code is governed by a GNU General Public License v3.0
license that can be found in the LICENSE file.
*/

import React from "react";
import {useForm} from "react-hook-form";
import {getURL} from "../utils";
import {Box, Button, Center, Flex, FormErrorMessage, IconButton, Text, Textarea} from "@chakra-ui/react";
import {ArrowUpIcon, DownloadIcon} from "@chakra-ui/icons";

type FormInput = 
{
    textToPreprocess: string,
    replacementsJson: string,
}

type ResponseValues = 
{
    errorLog: string,
    preprocessedText: string,
    preprocessingLog: string,
}

function KairyouPage() 
{
    const textRef = React.useRef<HTMLInputElement>(null);
    const jsonRef = React.useRef<HTMLInputElement>(null);

    const {register, handleSubmit, setValue, formState: {isSubmitting}} = useForm<FormInput>();

    const [response, setResponse] = React.useState<ResponseValues>();


    const onSubmit = async (data: FormInput) => 
    {
        const response = await fetch(getURL("/v1/kairyou"), {
            method: "POST",
            headers: 
            {
                "Content-Type": "application/json",
                "Authorization": import.meta.env.VITE_AUTHORIZATION
            },
            body: JSON.stringify(data)
        })

        if (!response.ok) 
        {
            const result: { message: string } = await response.json();
            throw new Error("Error Returned:" + result.message);
        }

        const result: ResponseValues = await response.json();
        setResponse(result);
    }

    const onUpload = async (event: React.ChangeEvent<HTMLInputElement>) => 
    {
        const file = event.target.files?.[0];


        if (!file)
        {
            return;
        }


        const input = await file.text()
        switch (file.type) 
        {
            case "text/plain":
                setValue("textToPreprocess", input)
                return
            case "application/json":
                setValue("replacementsJson", input)
                return
            default:
                throw new Error("Invalid file type")
        }

    };


    const downloadOutput = (input: 'preprocessing_log' | 'preprocessedText') => 
    {
        let content = '';
        if (input === 'preprocessing_log') 
        {
            content = response?.preprocessingLog|| '';
        } 
        else if (input === 'preprocessedText')
        {
            content = response?.preprocessedText || '';
        }
        else
        {
            throw new Error("Invalid input type")
        }

        if (!content) 
            {
            return;
        }

        const blob = new Blob([content], {type: "text/plain"});
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a") as HTMLAnchorElement;
        link.download = input + '.txt';
        link.href = url;
        link.click();
    }

    return (
        <>
            {/* Hidden file inputs. Will allow us to use styled buttons */}
            <input onChange={onUpload} ref={textRef} type={'file'} accept={'.txt'} hidden/>
            <input onChange={onUpload} ref={jsonRef} type={'file'} accept={'.json'} hidden/>
            <form onSubmit={handleSubmit(onSubmit)}>
                <Flex flex={1} gap={2}>
                    <Box flex={1}>
                        <Text mb='8px'>Text Input <IconButton variant={'ghost'} size={'xl'}
                                                              onClick={() => textRef.current?.click()}
                                                              aria-label={'Upload Text'} icon={<ArrowUpIcon/>}/> </Text>
                        <Textarea rows={20} size='sm' {...register("textToPreprocess", {required: true})} />
                    </Box>
                    <Box flex={1}>
                        <Text mb='8px'>JSON Input <IconButton variant={'ghost'} size={'xl'}
                                                              onClick={() => jsonRef.current?.click()}
                                                              aria-label={'Upload JSON'} icon={<ArrowUpIcon/>}/> </Text>
                        <Textarea rows={20} size='sm' {...register("replacementsJson", {required: true})} />
                    </Box>
                </Flex>

                <FormErrorMessage></FormErrorMessage>

                <Button
                    mb={17} mt={17} width='100%' type="submit"
                    bg={'orange.400'}
                    color={'white'}
                    _hover={{
                        bg: 'orange.500',
                    }}
                    isLoading={isSubmitting}
                >Submit</Button>
            </form>

            {response && (
                <>
                    <Flex mt={17} gap='2'>

                        <Box flex={1}>
                            <Text mb='8px'>Preprocessing Log <IconButton onClick={() => downloadOutput("preprocessing_log")} variant={'ghost'}
                                                                          size='xl' aria-label="Download preprocessing log"
                                                                          icon={<DownloadIcon/>}/> </Text>

                            <Box overflowY='scroll' height={200}>
                                <Text style={{whiteSpace: "pre-wrap"}}>
                                    {response?.preprocessingLog}
                                </Text>
                            </Box>
                        </Box>
                        {response.errorLog ? (
                                <Box flex={1}>
                                    <Text mb='8px'>Error Log</Text>

                                    <Box overflowY='scroll' height={200}>
                                        <Text style={{whiteSpace: "pre-wrap"}}>
                                            {response?.errorLog}
                                        </Text>
                                    </Box>
                                </Box>
                            ) :
                            (
                                <Box flex={1}>
                                    <Text mb='8px'>Output <IconButton onClick={() => downloadOutput("preprocessedText")} variant={'ghost'}
                                                                      size='xl' aria-label="Download output"
                                                                      icon={<DownloadIcon/>}/> </Text>

                                    <Box overflowY='scroll' height={200}>
                                        <Text style={{whiteSpace: "pre-wrap"}}>
                                            {response?.preprocessedText}
                                        </Text>
                                    </Box>
                                </Box>
                            )
                        }

                    </Flex>
                    <Center>
                        <Button onClick={() => setResponse(undefined)} mb={17} colorScheme="orange" variant='ghost'>Clear
                            Logs</Button>
                    </Center>
                </>
            )}


        </>
    );
}

export default KairyouPage;