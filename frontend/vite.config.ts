import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig(({ mode }) => {
  const isSaaS = mode === 'saas';
  
  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src'),
      },
    },
    define: {
      'import.meta.env.VITE_SaaS_MODE': JSON.stringify(isSaaS ? 'true' : 'false'),
    },
    server: {
      port: isSaaS ? 5176 : 5175,
      host: 'localhost',
      open: false,
      proxy: {
        '/api': {
          target: 'http://127.0.0.1:8001',
          changeOrigin: true,
          secure: false,
        },
        '/auth': {
          target: 'http://127.0.0.1:8001',
          changeOrigin: true,
          secure: false,
        },
      },
    },
    build: {
      outDir: isSaaS ? 'dist-saas' : 'dist',
    },
  };
});
