/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        roboto:  ['Roboto', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        apercu:  ['Apercu', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        archivo: ['ArchivoBlack', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        paytone: ['PaytoneOne', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      colors: {
        'bondi-blue': {
          DEFAULT: 'rgb(254 80 103)',
          400: 'rgb(254 121 138)',
          500: 'rgb(254 80 103)',
          600: 'rgb(220 50 75)',
        },
        'ghost': {
          300: 'rgb(242 243 245)',
          600: 'rgb(166 172 183)',
          900: 'rgb(81 88 100)',
        },
        'mercury': {
          500: 'rgb(230 230 230)',
        },
        'daintree': {
          600: 'rgb(254 80 103)',
          700: 'rgb(254 80 103)',
          800: 'rgb(0 0 0)',
        },
        'abbey': {
          DEFAULT: 'rgb(70 72 73)',
          50:  'rgb(161 164 165)',
          100: 'rgb(151 154 155)',
          400: 'rgb(90 93 94)',
          500: 'rgb(70 72 73)',
          600: 'rgb(43 44 44)',
          700: 'rgb(15 16 16)',
          800: 'rgb(0 0 0)',
        },
      },
    },
  },
  plugins: [],
}
