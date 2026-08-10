/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans:    ['Hanken Grotesk', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono:    ['JetBrains Mono', 'ui-monospace', 'monospace'],
        roboto:  ['Hanken Grotesk', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        apercu:  ['Hanken Grotesk', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        archivo: ['Hanken Grotesk', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        paytone: ['Hanken Grotesk', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      colors: {
        // ── ECSACONM brand (primary action colour) ──────────────────────────
        'brand':    'rgb(254 80 103)',
        'brand-dk': 'rgb(220 50 75)',

        // ── Material Design 3 surface / role tokens ──────────────────────────
        'surface':                   'var(--surface)',
        'surface-bright':            'var(--surface-bright)',
        'surface-dim':               'var(--surface-dim)',
        'surface-variant':           'var(--surface-variant)',
        'surface-container-lowest':  'var(--surface-container-lowest)',
        'surface-container-low':     'var(--surface-container-low)',
        'surface-container':         'var(--surface-container)',
        'surface-container-high':    'var(--surface-container-high)',
        'surface-container-highest': 'var(--surface-container-highest)',

        'on-surface':         'var(--on-surface)',
        'on-surface-variant': 'var(--on-surface-variant)',

        'outline':         'var(--outline)',
        'outline-variant': 'var(--outline-variant)',

        // ── Primary (brand red for interactive elements) ─────────────────────
        'cp-primary':    'rgb(254 80 103)',
        'cp-primary-dk': 'rgb(220 50 75)',
        'on-primary':    '#ffffff',
        'primary-container':    'var(--primary-container)',
        'on-primary-container': 'var(--on-primary-container)',

        // ── Secondary ────────────────────────────────────────────────────────
        'cp-secondary':           'var(--cp-secondary)',
        'secondary-container':    'var(--secondary-container)',
        'on-secondary-container': 'var(--on-secondary-container)',

        // ── Tertiary ─────────────────────────────────────────────────────────
        'cp-tertiary':           'var(--cp-tertiary)',
        'tertiary-container':    'var(--tertiary-container)',
        'on-tertiary-container': 'var(--on-tertiary-container)',

        // ── Error (for not-registered / alert states) ────────────────────────
        'cp-error':          'var(--cp-error)',
        'error-container':   'var(--error-container)',
        'on-error-container':'var(--on-error-container)',

        // ── Legacy aliases kept for backward compat ──────────────────────────
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
        'mercury': { 500: 'rgb(230 230 230)' },
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
