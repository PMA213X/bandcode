/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'bandcode': {
          'primary': '#06b6d4',
          'secondary': '#8b5cf6',
          'success': '#22c55e',
          'warning': '#eab308',
          'error': '#ef4444',
        }
      }
    }
  },
  plugins: [],
}
