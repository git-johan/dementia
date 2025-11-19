/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx}",
    "../src/**/*.{js,ts,jsx,tsx}", // Include the package source
  ],
  theme: {
    extend: {
      colors: {
        'chat': {
          'primary': '#007AFF',
          'secondary': '#f3f4f6',
          'accent': '#10b981',
        }
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'bounce-dots': 'bounceDots 1.4s infinite ease-in-out both',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        bounceDots: {
          '0%, 80%, 100%': {
            transform: 'scale(0)',
            opacity: '0.5'
          },
          '40%': {
            transform: 'scale(1)',
            opacity: '1'
          }
        }
      }
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
  darkMode: 'media',
}