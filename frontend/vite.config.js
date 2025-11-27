// vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  css: {
    postcss: './postcss.config.js' // Explicit path for Windows compatibility
  },
  server: {
    host: true, // Expose to all network interfaces (localhost, 127.0.0.1, etc.)
    hmr: {
      overlay: false // Disable error overlay if needed
    }
  }
})