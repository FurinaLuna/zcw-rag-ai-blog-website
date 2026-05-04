import type { Config } from "tailwindcss";

export default {
  content: [
    "./components/**/*.{vue,js,ts}",
    "./layouts/**/*.vue",
    "./pages/**/*.vue",
    "./app.vue",
  ],
  theme: {
    extend: {
      colors: {
        "bg-page": "#FAFAF7",
        "bg-surface": "#FFFFFF",
        "text-primary": "#1F2933",
        "text-secondary": "#667085",
        "text-tertiary": "#9CA3AF",
        "border-default": "#E4E0D8",
        accent: "#0F766E",
        "accent-warm": "#B7791F",
        "code-bg": "#111827",
        "code-text": "#E5E7EB",
      },
      maxWidth: {
        content: "680px",
        home: "1100px",
        admin: "1200px",
        ask: "800px",
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', "monospace"],
        serif: ['"Noto Serif SC"', "serif"],
      },
    },
  },
} satisfies Config;
