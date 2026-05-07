import { defineConfig } from "vitest/config";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  // @ts-ignore - vite version mismatch with vitest's bundled vite
  plugins: [vue()],
  test: {
    environment: "happy-dom",
    globals: true,
    setupFiles: ["./tests/setup.ts"],
    exclude: ["**/setup.ts", "e2e/**", "node_modules/**"],
  },
  resolve: {
    alias: {
      "~": __dirname,
    },
  },
  define: {
    "import.meta.client": "true",
  },
});
