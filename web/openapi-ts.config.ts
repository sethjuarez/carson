import { defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
  input: 'http://localhost:8000/openapi.json',
  output: './api',
  plugins: [
    // ...other plugins
    '@tanstack/react-query',
  ],
});