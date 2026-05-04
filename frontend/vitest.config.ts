import { defineConfig } from "vitest/config";

export default defineConfig({
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
