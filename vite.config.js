import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

// GitHub Pages 子路径
export default defineConfig({
  base: '/books/',
  plugins: [vue(), tailwindcss()],
  build: {
    outDir: 'dist',
  },
})
