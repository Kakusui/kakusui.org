import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

// https://vitejs.dev/config/
export default defineConfig(
{
  plugins: [react()],
  build: 
  {
    sourcemap: true, // Enable source maps
  },
  server: 
  {
    port: 5173, // Make sure this matches your development server port
  },

})
