// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// react
import { useEffect, useMemo, useState, useRef } from "react";

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
  Tab,
  Tabs,
  TabList,
  TabPanel,
  TabPanels,
  Box,
  Flex,
  Text,
  Center,
  Checkbox,
  NumberInput,
  NumberInputField,
  Slider,
  SliderTrack,
  SliderFilledTrack,
  SliderThumb
} from "@chakra-ui/react";

import { ArrowUpIcon } from "@chakra-ui/icons";

// components and custom things
import Turnstile from "../components/Turnstile";
import CopyButton from "../components/CopyButton";
import DownloadButton from "../components/DownloadButton";
import HowToUseSection from "../components/HowToUseSection";
import LegalLinks from "../components/LegalLinks";
function KudasaiPage() 
{
    useEffect(() => 
    {
        document.title = 'Kakusui | Kudasai';
    }, []);

    const [activeTab, setActiveTab] = useState(0);
    const [_____________, setTurnstileToken] = useState<string | null>(null);
    const [resetTurnstile, ________] = useState(false);
    const [translationMethod, setTranslationMethod] = useState("DeepL");
    const [apiKey, setApiKey] = useState("");

    // File upload refs
    const indexTextRef = useRef<HTMLInputElement>(null);
    const indexJsonRef = useRef<HTMLInputElement>(null);
    const knowledgeBaseFileRef = useRef<HTMLInputElement>(null);
    const knowledgeBaseDirRef = useRef<HTMLInputElement>(null);
    const preprocessTextRef = useRef<HTMLInputElement>(null);
    const translatorTextRef = useRef<HTMLInputElement>(null);

    // Form states
    const [indexedText, setIndexedText] = useState("");
    const [indexingResults, ____] = useState("");
    const [preprocessedText, setPreprocessedText] = useState("");
    const [preprocessingResults, _____] = useState("");
    const [translatedText, setTranslatedText] = useState("");
    const [jeCheckText, ___] = useState("");
    const [debugLog, _] = useState("");
    const [errorLog, __] = useState("");

    const onTurnstileVerify = (token: string) => 
    {
        setTurnstileToken(token);
    };

    const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>, setter: (value: string) => void) => 
    {
        const file = event.target.files?.[0];
        if (file) 
        {
            const reader = new FileReader();
            reader.onload = (e) => 
            {
                setter(e.target?.result as string);
            };
            reader.readAsText(file);
        }
    };

    const memoizedTurnstile = useMemo(() => 
        <Turnstile 
            siteKey="0x4AAAAAAAbu-SlGyNF03684" 
            onVerify={onTurnstileVerify} 
            resetKey={resetTurnstile} 
        />
    , [resetTurnstile]);

    return (
        <Box p={4}>
            <Tabs index={activeTab} onChange={setActiveTab}>
                <TabList>
                    <Tab>Kudasai</Tab>
                    <Tab>Name Indexing | Kairyou</Tab>
                    <Tab>Text Preprocessing | Kairyou</Tab>
                    <Tab>Text Translation | Translator</Tab>
                    <Tab>Translation Settings</Tab>
                    <Tab>Logging</Tab>
                    <Tab>Output</Tab>
                </TabList>

                <TabPanels>
                    {/* Main Kudasai Tab */}
                    <TabPanel>
                        <Text fontSize="xl">Welcome to Kudasai</Text>
                    </TabPanel>

                    {/* Name Indexing Tab */}
                    <TabPanel>
                        <Flex gap={4}>
                            <VStack flex={1} align="stretch">
                                <FormControl>
                                    <FormLabel>TXT file with Japanese Text</FormLabel>
                                    <Input type="file" display="none" ref={indexTextRef} onChange={(e) => handleFileUpload(e, setIndexedText)} />
                                    <Button onClick={() => indexTextRef.current?.click()} leftIcon={<ArrowUpIcon />}>
                                        Upload Text File
                                    </Button>
                                </FormControl>

                                <FormControl>
                                    <FormLabel>Replacements JSON file</FormLabel>
                                    <Input type="file" display="none" ref={indexJsonRef} />
                                    <Button onClick={() => indexJsonRef.current?.click()} leftIcon={<ArrowUpIcon />}>
                                        Upload JSON File
                                    </Button>
                                </FormControl>

                                <FormControl>
                                    <FormLabel>Knowledge Base Single File</FormLabel>
                                    <Input type="file" display="none" ref={knowledgeBaseFileRef} />
                                    <Button onClick={() => knowledgeBaseFileRef.current?.click()} leftIcon={<ArrowUpIcon />}>
                                        Upload Knowledge Base File
                                    </Button>
                                </FormControl>

                                <FormControl>
                                    <FormLabel>Knowledge Base Directory</FormLabel>
                                    <Input type="file" display="none" ref={knowledgeBaseDirRef} />
                                    <Button onClick={() => knowledgeBaseDirRef.current?.click()} leftIcon={<ArrowUpIcon />}>
                                        Upload Directory
                                    </Button>
                                </FormControl>

                                <HStack>
                                    <Button colorScheme="blue">Run</Button>
                                    <Button colorScheme="red">Clear</Button>
                                </HStack>

                                <Button colorScheme="green">Send to Preprocessing (Kairyou)</Button>
                            </VStack>

                            <VStack flex={1} align="stretch">
                                <FormControl>
                                    <FormLabel>
                                        Indexed text
                                        <CopyButton text={indexedText} />
                                        <DownloadButton text={indexedText} fileName="indexed_text.txt" />
                                    </FormLabel>
                                    <Textarea value={indexedText} isReadOnly height="300px" />
                                </FormControl>
                            </VStack>

                            <VStack flex={1} align="stretch">
                                <FormControl>
                                    <FormLabel>
                                        Indexing Results
                                        <CopyButton text={indexingResults} />
                                        <DownloadButton text={indexingResults} fileName="indexing_results.txt" />
                                    </FormLabel>
                                    <Textarea value={indexingResults} isReadOnly height="300px" />
                                </FormControl>
                            </VStack>
                        </Flex>
                    </TabPanel>

                    {/* Text Preprocessing Tab */}
                    <TabPanel>
                        <Flex gap={4}>
                            <VStack flex={1} align="stretch">
                                <FormControl>
                                    <FormLabel>TXT file with Japanese Text</FormLabel>
                                    <Input type="file" display="none" ref={preprocessTextRef} onChange={(e) => handleFileUpload(e, setPreprocessedText)} />
                                    <Button onClick={() => preprocessTextRef.current?.click()} leftIcon={<ArrowUpIcon />}>
                                        Upload Text File
                                    </Button>
                                </FormControl>

                                <FormControl>
                                    <FormLabel>Japanese Text</FormLabel>
                                    <Textarea placeholder="Use this or the text file input..." height="150px" />
                                </FormControl>

                                <HStack>
                                    <Button colorScheme="blue">Run</Button>
                                    <Button colorScheme="red">Clear</Button>
                                </HStack>

                                <Button colorScheme="green">Send to Translator</Button>
                            </VStack>

                            <VStack flex={1} align="stretch">
                                <FormControl>
                                    <FormLabel>
                                        Preprocessed text
                                        <CopyButton text={preprocessedText} />
                                        <DownloadButton text={preprocessedText} fileName="preprocessed_text.txt" />
                                    </FormLabel>
                                    <Textarea value={preprocessedText} isReadOnly height="300px" />
                                </FormControl>
                            </VStack>

                            <VStack flex={1} align="stretch">
                                <FormControl>
                                    <FormLabel>
                                        Preprocessing Results
                                        <CopyButton text={preprocessingResults} />
                                        <DownloadButton text={preprocessingResults} fileName="preprocessing_results.txt" />
                                    </FormLabel>
                                    <Textarea value={preprocessingResults} isReadOnly height="300px" />
                                </FormControl>
                            </VStack>
                        </Flex>
                    </TabPanel>

                    {/* Text Translation Tab */}
                    <TabPanel>
                        <Flex gap={4}>
                            <VStack flex={1} align="stretch">
                                <FormControl>
                                    <FormLabel>TXT file with Japanese Text</FormLabel>
                                    <Input type="file" display="none" ref={translatorTextRef} onChange={(e) => handleFileUpload(e, setTranslatedText)} />
                                    <Button onClick={() => translatorTextRef.current?.click()} leftIcon={<ArrowUpIcon />}>
                                        Upload Text File
                                    </Button>
                                </FormControl>

                                <FormControl>
                                    <FormLabel>Translation Method</FormLabel>
                                    <Select value={translationMethod} onChange={(e) => setTranslationMethod(e.target.value)}>
                                        <option value="OpenAI">OpenAI</option>
                                        <option value="Gemini">Gemini</option>
                                        <option value="DeepL">DeepL</option>
                                        <option value="Google Translate">Google Translate</option>
                                    </Select>
                                </FormControl>

                                <FormControl>
                                    <FormLabel>API Key</FormLabel>
                                    <Input type="password" value={apiKey} onChange={(e) => setApiKey(e.target.value)} />
                                </FormControl>

                                <HStack>
                                    <Button colorScheme="blue">Translate</Button>
                                    <Button colorScheme="green">Calculate Cost</Button>
                                    <Button colorScheme="red">Clear</Button>
                                </HStack>
                            </VStack>

                            <VStack flex={1} align="stretch">
                                <FormControl>
                                    <FormLabel>
                                        Translated Text
                                        <CopyButton text={translatedText} />
                                        <DownloadButton text={translatedText} fileName="translated_text.txt" />
                                    </FormLabel>
                                    <Textarea value={translatedText} isReadOnly height="300px" />
                                </FormControl>
                            </VStack>

                            <VStack flex={1} align="stretch">
                                <FormControl>
                                    <FormLabel>
                                        JE Check Text
                                        <CopyButton text={jeCheckText} />
                                        <DownloadButton text={jeCheckText} fileName="je_check_text.txt" />
                                    </FormLabel>
                                    <Textarea value={jeCheckText} isReadOnly height="300px" />
                                </FormControl>
                            </VStack>
                        </Flex>

                        <Center mt={4}>
                            {memoizedTurnstile}
                        </Center>
                    </TabPanel>

                    {/* Translation Settings Tab */}
                    <TabPanel>
                        <VStack spacing={4} align="stretch">
                            <Text fontSize="xl">Base Translation Settings</Text>
                            
                            <FormControl>
                                <FormLabel>Prompt Assembly Mode</FormLabel>
                                <Select defaultValue="1">
                                    <option value="1">Mode 1</option>
                                    <option value="2">Mode 2</option>
                                </Select>
                            </FormControl>

                            <FormControl>
                                <FormLabel>Number of Lines Per Batch</FormLabel>
                                <NumberInput defaultValue={5}>
                                    <NumberInputField />
                                </NumberInput>
                            </FormControl>

                            <FormControl>
                                <FormLabel>Temperature</FormLabel>
                                <Slider defaultValue={0.7} min={0} max={1} step={0.1}>
                                    <SliderTrack>
                                        <SliderFilledTrack />
                                    </SliderTrack>
                                    <SliderThumb />
                                </Slider>
                            </FormControl>

                            <FormControl>
                                <FormLabel>Gender Context Insertion</FormLabel>
                                <Checkbox defaultChecked>Enable</Checkbox>
                            </FormControl>

                            <HStack>
                                <Button colorScheme="blue">Apply Changes</Button>
                                <Button>Reset to Default</Button>
                                <Button>Discard Changes</Button>
                            </HStack>
                        </VStack>
                    </TabPanel>

                    {/* Logging Tab */}
                    <TabPanel>
                        <VStack spacing={4} align="stretch">
                            <FormControl>
                                <FormLabel>
                                    Debug Log
                                    <CopyButton text={debugLog} />
                                    <DownloadButton text={debugLog} fileName="debug_log.txt" />
                                </FormLabel>
                                <Textarea value={debugLog} isReadOnly height="200px" />
                            </FormControl>

                            <FormControl>
                                <FormLabel>
                                    Error Log
                                    <CopyButton text={errorLog} />
                                    <DownloadButton text={errorLog} fileName="error_log.txt" />
                                </FormLabel>
                                <Textarea value={errorLog} isReadOnly height="200px" />
                            </FormControl>

                            <Button colorScheme="red">Clear Logs</Button>
                        </VStack>
                    </TabPanel>

                    {/* Output Tab */}
                    <TabPanel>
                        <Center>
                            <Button colorScheme="blue">Download All Outputs</Button>
                        </Center>
                    </TabPanel>
                </TabPanels>
            </Tabs>

            <HowToUseSection
                repositoryUrl="https://github.com/Bikatr7/Kudasai"
                steps={[
                    "Select the appropriate tab for your needs (Indexing, Preprocessing, or Translation).",
                    "Upload or input the required files and text.",
                    "Configure the settings as needed.",
                    "Run the process and review the results.",
                    "Download or copy the output as needed."
                ]}
                notes={[
                    "Turnstile verification is required for translation services.",
                    "API keys are required for OpenAI, Gemini, and DeepL services.",
                    "Please be mindful of API usage and costs."
                ]}
                contactEmail="contact@kakusui.org"
            />

            <LegalLinks basePath="/kudasai" />
        </Box>
    );
}

export default KudasaiPage; 