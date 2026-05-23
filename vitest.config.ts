import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    include: ['**/*.test.ts', '**/*.test.tsx'],
    environment: 'jsdom',
    setupFiles: [
      './apps/web/src/test/setup.ts',
    ],
    globals: true,
  },
});
