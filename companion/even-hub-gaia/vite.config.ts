import { defineConfig, loadEnv } from 'vite'

// The glasses run this app inside the Even Hub companion app's WebView, loaded from this
// dev server over the LAN. To reach the Gaia API without CORS or mixed-content trouble, the
// app calls a SAME-ORIGIN path (/gaia/...) and Vite proxies it server-side to the real API.
// So the phone only ever talks to this dev server; this dev server talks to Gaia.
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const gaiaTarget = env.GAIA_API_TARGET || 'http://127.0.0.1:8000'
  return {
    server: {
      host: true,        // bind 0.0.0.0 so the phone/glasses can load it over the LAN
      port: 5173,
      proxy: {
        '/gaia': {
          target: gaiaTarget,
          changeOrigin: true,
          rewrite: (p) => p.replace(/^\/gaia/, ''),
        },
      },
    },
    build: { target: 'esnext' },
  }
})
