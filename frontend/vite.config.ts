// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => 
{

  if(mode === 'production') 
  {
    process.env.NODE_ENV = 'production';
  } 
  else 
  {
    process.env.NODE_ENV = 'development';
  }

  return {
    plugins: [react()],
    build: {
      sourcemap: true, 
    },
    server: {
      port: 5173, // Dev server port
    },
  }
})
