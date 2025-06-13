/** @type {import('tailwindcss').Config} */
export default {
  // Configure files to scan for Tailwind classes
  content: [
    "./index.html", // Include your main HTML file
    "./src/**/*.{js,ts,jsx,tsx}", // Scan all JS, TS, JSX, TSX files in the src directory and its subdirectories
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
