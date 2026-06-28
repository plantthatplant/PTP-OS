import { defineConfig, loadEnv } from 'vite'

// Dev only: proxy /gaia → the Gaia API so the simulator avoids CORS.
// On device, the plugin calls VITE_GAIA_API_URL directly (see src/gaia.ts).
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const target = env.VITE_GAIA_API_URL || 'http://127.0.0.1:8000'
  return {
    server: {
      port: 5173,
      proxy: {
        '/gaia': {
          target,
          changeOrigin: true,
          rewrite: (p) => p.replace(/^\/gaia/, ''),
        },
      },
    },
  }
})
