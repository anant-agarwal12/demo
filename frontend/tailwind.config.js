/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'friendly': '#10b981',
        'unknown': '#ef4444',
        'suspicious': '#f59e0b'
      }
    },
  },
  plugins: [],
}
