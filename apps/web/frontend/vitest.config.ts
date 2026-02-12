import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    globals: true,
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@design-system/tokens/tokens': path.resolve(
        __dirname,
        '../../..',
        'packages/ui-kit/design-system/tokens/tokens.ts'
      ),
      '@design-system/icons/icon-map.json': path.resolve(
        __dirname,
        '../../..',
        'packages/ui-kit/design-system/icons/icon-map.json'
      ),
    },
  },
});
