import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#070908",
        coal: "#101614",
        moss: "#14231f",
        chalk: "#f0eadb",
        parchment: "#d8c9aa",
        copper: "#d29355",
        mint: "#7dd7ba",
        ice: "#bfe8ff",
      },
      fontFamily: {
        sans: ["var(--font-sans)", "Avenir Next", "Trebuchet MS", "sans-serif"],
        display: ["var(--font-display)", "Georgia", "serif"],
      },
      boxShadow: {
        glow: "0 0 60px rgba(125, 215, 186, 0.18)",
      },
    },
  },
  plugins: [],
};

export default config;
