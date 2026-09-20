/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0b0e14',
        card: '#131822',
        accent: '#1e2638',
        border: '#242e42',
        primary: '#3b82f6',
      },
    },
  },
  plugins: [],
}
