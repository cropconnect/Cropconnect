import path from "path";
import { fileURLToPath } from "url";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: "autoUpdate",
      includeAssets: ["favicon.ico", "og-image.svg"],
      manifest: {
        name: "CropConnect",
        short_name: "CropConnect",
        description: "Smart farming dashboard - soil to screen.",
        theme_color: "#1B4332",
        background_color: "#FDFBF7",
        display: "standalone",
        orientation: "portrait",
        start_url: "/",
        icons: [
          { src: "/icon.svg", sizes: "any", type: "image/svg+xml" },
          { src: "/icon.svg", sizes: "any", type: "image/svg+xml", purpose: "maskable" },
        ],
      },
      workbox: {
        globPatterns: ["**/*.{js,css,html,ico,png,svg,woff2}"],
        runtimeCaching: [
          {
            urlPattern: ({ url }) => url.pathname.startsWith("/api/sensors") || url.pathname.startsWith("/api/weather"),
            handler: "StaleWhileRevalidate",
            options: {
              cacheName: "api-sensor-weather",
              expiration: { maxEntries: 50, maxAgeSeconds: 300 },
            },
          },
          {
            urlPattern: ({ url }) => url.pathname.startsWith("/api/market"),
            handler: "StaleWhileRevalidate",
            options: {
              cacheName: "api-market",
              expiration: { maxEntries: 20, maxAgeSeconds: 3600 },
            },
          },
        ],
      },
    }),
  ],
  envPrefix: "VITE_",
  test: {
    environment: "jsdom",
    setupFiles: "./src/test/setup.js",
    exclude: ["node_modules", "build", "e2e"],
    globals: true,
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
  },
});
