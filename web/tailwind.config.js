/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      keyframes: {
        roll: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(720deg)' },
        },
      },
      animation: {
        roll: 'roll 0.6s ease-in-out',
      },
    },
  },
  plugins: [],
}

