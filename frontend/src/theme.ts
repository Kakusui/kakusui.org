// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

// chakra-ui
import { extendTheme, type ThemeConfig } from '@chakra-ui/react'

const config: ThemeConfig = 
{
    initialColorMode: 'dark',
    useSystemColorMode: false,
}

const theme = extendTheme(
{
    config,
    styles: 
    {
        global: 
        {
            'html, body': 
            {
                bg: '#14192b',
            },
        },
    },
})

export default theme