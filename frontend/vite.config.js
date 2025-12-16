import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
      },
      // Copia Bootstrap Italia nel build
      output: {
        assetFileNames: (assetInfo) => {
          if (assetInfo.name.includes('bootstrap-italia')) {
            return 'assets/bootstrap-italia/[name]-[hash][extname]'
          }
          return 'assets/[name]-[hash][extname]'
        }
      }
    }
  },
  // Assicura che node_modules/bootstrap-italia sia accessibile
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    }
  }
})