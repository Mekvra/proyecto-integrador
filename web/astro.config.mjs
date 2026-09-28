// @ts-check
import { defineConfig, fontProviders } from 'astro/config';

export default defineConfig({
  site: 'https://mekvra.github.io',
  base: '/proyecto-integrador',
  fonts: [
    {
      provider: fontProviders.fontshare(),
      name: 'Switzer',
      cssVariable: '--font-switzer',
      weights: [400, 500],
      fallbacks: ['General Sans', 'ui-sans-serif', 'system-ui', 'sans-serif'],
    },
    {
      provider: fontProviders.google(),
      name: 'Geist Mono',
      cssVariable: '--font-geist-mono',
      weights: [400],
      fallbacks: ['ui-monospace', 'Consolas', 'monospace'],
    },
  ],
});
