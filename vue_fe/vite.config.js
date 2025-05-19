// vite.config.js
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      "/stt": {
        target: "http://127.0.0.1:8005",
        changeOrigin: true,
      },
      "/tts": {
        target: "http://127.0.0.1:8005",
        changeOrigin: true,
      },
      "/call-center": {
        target: "http://127.0.0.1:8005",
        changeOrigin: true,
      }
    },
  },
});
