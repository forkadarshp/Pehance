/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        // Sophisticated warm neutral palette
        'warm-gray': {
          50: '#fafaf9',
          100: '#f5f5f4',
          200: '#e7e5e4',
          300: '#d6d3d1',
          400: '#a8a29e',
          500: '#78716c',
          600: '#57534e',
          700: '#44403c',
          800: '#292524',
          900: '#1c1917',
        },
        // Muted amber accent system
        'accent': {
          50: '#fefbf3',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
          800: '#92400e',
          900: '#78350f',
        }
      },
      fontFamily: {
        'display': ['Inter', 'SF Pro Display', 'system-ui', 'sans-serif'],
        'body': ['Inter', 'system-ui', 'sans-serif'],
        'mono': ['SF Mono', 'JetBrains Mono', 'monospace'],
      },
      fontSize: {
        'display-large': ['clamp(3rem, 8vw, 6rem)', { lineHeight: '0.9', letterSpacing: '-0.025em' }],
        'display-medium': ['clamp(2rem, 5vw, 3.5rem)', { lineHeight: '1.1', letterSpacing: '-0.02em' }],
        'heading-large': ['clamp(1.5rem, 3vw, 2.25rem)', { lineHeight: '1.3', letterSpacing: '-0.015em' }],
        'heading-medium': ['1.5rem', { lineHeight: '1.4', letterSpacing: '-0.01em' }],
        'body-large': ['1.125rem', { lineHeight: '1.7' }],
        'body': ['1rem', { lineHeight: '1.6' }],
        'caption': ['0.875rem', { lineHeight: '1.5', letterSpacing: '0.01em' }],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      boxShadow: {
        'sophisticated': '0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24)',
        'elevated': '0 14px 28px rgba(0, 0, 0, 0.25), 0 10px 10px rgba(0, 0, 0, 0.22)',
        'inset-soft': 'inset 0 2px 4px rgba(0, 0, 0, 0.1)',
        'accent-glow': '0 4px 14px rgba(217, 119, 6, 0.25)',
      },
      borderRadius: {
        'sophisticated': '0.75rem',
        'elegant': '1rem',
        'premium': '1.5rem',
      },
      animation: {
        'subtle-fade-in': 'subtleFadeIn 400ms cubic-bezier(0.4, 0, 0.2, 1) forwards',
        'gentle-slide-up': 'gentleSlideUp 500ms cubic-bezier(0.4, 0, 0.2, 1) forwards',
        'elegant-reveal': 'elegantReveal 600ms cubic-bezier(0.4, 0, 0.2, 1) forwards',
        'subtle-pulse': 'subtlePulse 2s ease-in-out infinite',
        'gentle-float': 'gentleFloat 3s ease-in-out infinite',
      },
      keyframes: {
        subtleFadeIn: {
          from: { opacity: '0', transform: 'translateY(8px)' },
          to: { opacity: '1', transform: 'translateY(0)' }
        },
        gentleSlideUp: {
          from: { opacity: '0', transform: 'translateY(16px) scale(0.98)' },
          to: { opacity: '1', transform: 'translateY(0) scale(1)' }
        },
        elegantReveal: {
          from: { opacity: '0', transform: 'translateY(12px)' },
          to: { opacity: '1', transform: 'translateY(0)' }
        },
        subtlePulse: {
          '0%, 100%': { opacity: '0.8' },
          '50%': { opacity: '1' }
        },
        gentleFloat: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-4px)' }
        }
      },
      transitionTimingFunction: {
        'sophisticated': 'cubic-bezier(0.4, 0, 0.2, 1)',
      },
      backdropBlur: {
        'sophisticated': '20px',
      }
    },
  },
  plugins: [],
};