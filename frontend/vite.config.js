// vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  css: {
    postcss: './postcss.config.js' // Explicit path for Windows compatibility
  },
  server: {
    hmr: {
      overlay: false // Disable error overlay if needed
    }
  }
})