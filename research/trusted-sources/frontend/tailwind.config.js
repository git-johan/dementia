/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    './src/hooks/**/*.{js,ts,jsx,tsx}',
    './src/providers/**/*.{js,ts,jsx,tsx}',
    './src/utils/**/*.{js,ts,jsx,tsx}',
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
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' }
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
  darkMode: 'media',
  plugins: [
    require('@tailwindcss/typography'),
  ],
}