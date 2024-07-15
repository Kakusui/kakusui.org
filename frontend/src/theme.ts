/*
Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
Use of this source code is governed by an GNU Affero General Public License v3.0
license that can be found in the LICENSE file.
*/

// 1. import `extendTheme` function
import {extendTheme, type ThemeConfig} from '@chakra-ui/react'

// 2. Add your color mode config
const config: ThemeConfig = 
{
    initialColorMode: 'dark',
    useSystemColorMode: false,
}

// 3. extend the theme
const theme = extendTheme({config})

export default theme