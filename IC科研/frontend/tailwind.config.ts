import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        canvas: "rgb(var(--canvas) / <alpha-value>)",
        panel: "rgb(var(--panel) / <alpha-value>)",
        line: "rgb(var(--line) / <alpha-value>)",
        ink: "rgb(var(--ink) / <alpha-value>)",
        muted: "rgb(var(--muted) / <alpha-value>)",
        accent: "rgb(var(--accent) / <alpha-value>)",
        signal: "rgb(var(--signal) / <alpha-value>)",
      },
      fontFamily: {
        sans: ["var(--font-inter)", "var(--font-noto)", "system-ui", "sans-serif"],
        mono: ["var(--font-jetbrains)", "Consolas", "monospace"],
      },
      boxShadow: {
        panel: "0 22px 65px rgba(8, 17, 31, 0.08)",
      },
      backgroundImage: {
        grid: "linear-gradient(to right, rgb(var(--line) / .28) 1px, transparent 1px), linear-gradient(to bottom, rgb(var(--line) / .28) 1px, transparent 1px)",
      },
    },
  },
  plugins: [],
};

export default config;

