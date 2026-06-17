import { defineConfig } from 'vite';

// Статика, относительные пути — чтобы собранный билд открывался откуда угодно.
export default defineConfig({
  base: './',
  server: {
    host: true,
    open: true,
  },
});
