/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0F172A',
        primary: '#06B6D4',
        accent: '#14B8A6',
        textMain: '#F8FAFC',
      }
    },
  },
  plugins: [],
}
