/*
Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
Use of this source code is governed by an GNU Affero General Public License v3.0
license that can be found in the LICENSE file.
*/

import React from 'react';
import { IconButton } from '@chakra-ui/react';
import { DownloadIcon } from '@chakra-ui/icons';

interface DownloadButtonProps {
    text: string;
    fileName: string;
}

const DownloadButton: React.FC<DownloadButtonProps> = ({ text, fileName }) => {
    const handleDownload = () => {
        const blob = new Blob([text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.download = `${fileName}.txt`;
        link.href = url;
        link.click();
    };

    return (
        <IconButton
            onClick={handleDownload}
            variant="ghost"
            size="xl"
            aria-label="Download text"
            icon={<DownloadIcon />}
        />
    );
};

export default DownloadButton;
