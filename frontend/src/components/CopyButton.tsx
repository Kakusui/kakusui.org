import React, { useState } from 'react';
import { IconButton } from '@chakra-ui/react';
import { CopyIcon, CheckIcon } from '@chakra-ui/icons';
import { useClipboard } from '@chakra-ui/react';

interface CopyButtonProps {
    text: string;
}

const CopyButton: React.FC<CopyButtonProps> = ({ text }) => {
    const { onCopy } = useClipboard(text);
    const [copyIcon, setCopyIcon] = useState(<CopyIcon />);

    const handleCopy = () => {
        onCopy();
        setCopyIcon(<CheckIcon color="green.500" />);
        setTimeout(() => setCopyIcon(<CopyIcon />), 2000);
    };

    return (
        <IconButton
            onClick={handleCopy}
            variant="ghost"
            size="xl"
            aria-label="Copy text"
            icon={copyIcon}
        />
    );
};

export default CopyButton;
