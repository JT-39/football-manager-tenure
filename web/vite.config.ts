import path from 'node:path'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  // The site lives at https://<user>.github.io/football-manager-tenure/, so every
  // asset link must start with this folder name. Locally it is served at "/".
  base: process.env.GITHUB_ACTIONS ? '/football-manager-tenure/' : '/',
  plugins: [react(), tailwindcss()],
  resolve: {
    // "@/components/x" means "src/components/x"
    alias: { '@': path.resolve(__dirname, './src') },
  },
})
