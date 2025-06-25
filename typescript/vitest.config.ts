import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'node',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'dist/',
        'coverage/',
        'src/generated/',
        '**/*.test.ts',
        '**/*.spec.ts'
      ]
    },
    include: ['tests/**/*.test.ts'],
    exclude: ['node_modules/', 'dist/'],
    globals: true
  }
});