import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',

  // Run tests one at a time so they don't interfere with each other
  fullyParallel: false,
  workers: 1,

  // Fail the build on CI if you accidentally left test.only in the source
  forbidOnly: !!process.env.CI,

  // Retry once on CI so flaky network calls don't fail the whole run
  retries: process.env.CI ? 1 : 0,

  reporter: 'html',

  use: {
    // All page.goto('/') calls resolve against this base URL
    baseURL: process.env.BASE_URL ?? 'http://localhost:3000',

    // Save a trace on the first retry so you can debug failures
    trace: 'on-first-retry',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  // Auto-start the Next.js dev server before any test runs.
  // Locally: reuses a server already on port 3000 so you don't need two terminals.
  // CI: always starts a fresh server.
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
