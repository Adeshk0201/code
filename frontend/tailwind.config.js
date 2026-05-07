export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        clinical: {
          50: '#f0f7ff',
          100: '#e0efff',
          500: '#2563eb',
          600: '#1d4ed8',
          900: '#0f172a',
        }
      }
    }
  },
  plugins: []
}