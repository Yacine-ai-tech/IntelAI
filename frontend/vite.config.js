import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Dev API target. Defaults to a local backend; set VITE_PROXY_TARGET to develop the
// frontend against a remote/staging backend (e.g. the live deployment) without CORS.
const PROXY_TARGET = process.env.VITE_PROXY_TARGET || 'http://localhost:8000'

export default defineConfig({
  plugins: [
    react({
      // Babel fast-refresh stays enabled in dev only
      babel: { plugins: [] },
    }),
  ],

  // ── Dev server ────────────────────────────────────────────────────
  server: {
    port: 5173,
    strictPort: true,
    proxy: {
      '/api': {
        target: PROXY_TARGET,
        changeOrigin: true,
        ws: true,            // proxy WebSocket (/api/v1/ws/chat) to the backend
      },
      '/health': {
        target: PROXY_TARGET,
        changeOrigin: true,
      },
      '/metrics': {
        target: PROXY_TARGET,
        changeOrigin: true,
      },
    },
  },

  // ── Production build ──────────────────────────────────────────────
  build: {
    outDir: 'dist',
    sourcemap: false,
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
        passes: 2,
      },
    },
    // Keep individual chunks below 500 kB for fast initial load
    chunkSizeWarningLimit: 500,
    rollupOptions: {
      output: {
        manualChunks: {
          // React core — cached forever
          'vendor-react':   ['react', 'react-dom', 'react-router-dom'],
          // Charts — lazy loaded per page
          'vendor-charts':  ['recharts'],
          // Icons — tree-shaken, separate chunk
          'vendor-icons':   ['lucide-react'],
          // HTTP client
          'vendor-axios':   ['axios'],
        },
        // Stable cache-busting names
        chunkFileNames:  'assets/[name]-[hash].js',
        entryFileNames:  'assets/[name]-[hash].js',
        assetFileNames:  'assets/[name]-[hash][extname]',
      },
    },
  },

  // ── CSS performance ───────────────────────────────────────────────
  css: {
    devSourcemap: false,
  },
})
