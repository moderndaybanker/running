import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}'
  ],
  theme: {
    extend: {
      colors: {
        slateDeep: '#0b1220',
        panel: '#111a2e',
        accent: '#34d399',
        accentSoft: '#6ee7b7'
      },
      boxShadow: {
        glow: '0 0 0 1px rgba(110, 231, 183, 0.25), 0 10px 30px rgba(0, 0, 0, 0.35)'
      }
    }
  },
  plugins: []
};

export default config;
