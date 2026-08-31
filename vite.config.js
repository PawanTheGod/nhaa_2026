import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  base: '/nhaa_2026/',
  plugins: [
    tailwindcss(),
    react(),
  ],
})


