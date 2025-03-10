import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Local dev proxies /v1 to the Flask API so cookies and CORS behave like prod.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/v1": {
        target: process.env.VITE_API_PROXY_TARGET || "http://localhost:5000",
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: "dist",
    sourcemap: false,
    // TODO(aiko): split the maps chunk once MapView is lazy-loaded everywhere
    chunkSizeWarningLimit: 900,
  },
});
