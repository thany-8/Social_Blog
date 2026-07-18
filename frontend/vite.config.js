import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "path";

// Build React "islands" into the Flask app's static folder. Flask reads the
// generated manifest (dist/.vite/manifest.json) to inject the hashed bundle.
export default defineConfig({
  plugins: [react()],
  base: "/static/dist/",
  build: {
    outDir: resolve(__dirname, "../socialblog/static/dist"),
    emptyOutDir: true,
    manifest: true,
    rollupOptions: {
      input: resolve(__dirname, "src/main.jsx"),
    },
  },
});
