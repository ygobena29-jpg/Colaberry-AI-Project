import { test, expect } from '@playwright/test';

// Use a unique email per test run so we never collide with a previously registered
// user that might have a different password.
// Override with TEST_EMAIL env var when you need a stable address across runs.
const API_URL       = process.env.API_URL       ?? 'http://localhost:8080';

const TEST_EMAIL = process.env.TEST_EMAIL ?? `playwright-${Date.now()}@example.com`;
const TEST_PASSWORD = process.env.TEST_PASSWORD ?? 'Test1234!';

// ── Setup ────────────────────────────────────────────────────────────────────

// Register the test user once before all tests run.
// 200/201 = user created, 409 = already exists with this exact password (fine).
test.beforeAll(async ({ request }) => {
  const res = await request.post(`${API_URL}/auth/register`, {
    data: { email: TEST_EMAIL, password: TEST_PASSWORD },
  });
  console.log('[beforeAll] register status:', res.status(), 'email:', TEST_EMAIL);
  expect([200, 201, 409]).toContain(res.status());
});

// Clear localStorage before every test so each one starts from a logged-out state.
test.beforeEach(async ({ page }) => {
  await page.goto('/');
  await page.evaluate(() => localStorage.clear());
  await page.reload();
});

// ── Helpers ──────────────────────────────────────────────────────────────────

async function login(page: import('@playwright/test').Page) {
  // Start listening for the login response BEFORE the click so we don't miss it.
  const responsePromise = page.waitForResponse(
    (res) => res.url().includes('/auth/login') && res.request().method() === 'POST',
  );

  await page.fill('input[type="email"]', TEST_EMAIL);
  await page.fill('input[type="password"]', TEST_PASSWORD);
  await page.click('button:has-text("Login")');

  // Capture and log the actual API response for easy debugging.
  const loginResponse = await responsePromise;
  const loginBody = await loginResponse.json().catch(() => null);
  console.log('[login] status:', loginResponse.status(), 'body:', loginBody);

  await expect(page.getByText('Projects', { exact : true })).toBeVisible();
}

// ── Auth tests ───────────────────────────────────────────────────────────────

test('login stores a JWT token in localStorage', async ({ page }) => {
  await login(page);

  const token = await page.evaluate(() => localStorage.getItem('token'));
  expect(token).not.toBeNull();
  expect(token!.length).toBeGreaterThan(0);
});

test('logout clears the token and returns to the login form', async ({ page }) => {
  await login(page);

  await page.click('button:has-text("Logout")');

  await expect(page.getByText('Sign In')).toBeVisible();

  const token = await page.evaluate(() => localStorage.getItem('token'));
  expect(token).toBeNull();
});

test('page refresh keeps a logged-in user on the dashboard', async ({ page }) => {
  await login(page);

  await page.reload();

  await expect(page.getByText('Projects', { exact: true })).toBeVisible();
  const token = await page.evaluate(() => localStorage.getItem('token'));
  expect(token).not.toBeNull();
});

// Criterion 7: project data reloads after a page refresh (not just the dashboard heading).
test('page refresh reloads project data for the logged-in user', async ({ page, request }) => {
  // Acquire an API token inline so we can pre-create a project without touching the UI.
  const loginRes = await request.post(`${API_URL}/auth/login`, {
    data: { email: TEST_EMAIL, password: TEST_PASSWORD },
  });
  expect(loginRes.ok()).toBeTruthy();
  const { access_token } = await loginRes.json();

  const projectName = `E2E Refresh ${Date.now()}`;
  const createRes = await request.post(`${API_URL}/projects/`, {
    headers: { Authorization: `Bearer ${access_token}` },
    data: { name: projectName, description: '', tags: [] },
  });
  expect(createRes.ok()).toBeTruthy();

  // Log in via the UI — projects load automatically on login (criterion 2).
  await login(page);
  // Confirm the project is visible before the reload.
  await expect(page.getByText(projectName)).toBeVisible();

  // Register the listener BEFORE reload — useEffect calls getProjects() immediately
  // on mount via Promise.resolve().then(), so the GET can fire before we attach.
  const projectsAfterReload = page.waitForResponse(
    (res) => res.url().includes('/projects/') && res.request().method() === 'GET',
  );

  await page.reload();

  // Session must survive: dashboard still visible, token still in storage.
  await expect(page.getByText('Projects', { exact: true })).toBeVisible();
  const token = await page.evaluate(() => localStorage.getItem('token'));
  expect(token).not.toBeNull();

  // The post-reload fetch must succeed and the known project must still be visible.
  const projectsResponse = await projectsAfterReload;
  expect(projectsResponse.status()).toBe(200);
  await expect(page.getByText(projectName)).toBeVisible();
});

test('invalid token is cleared and user is returned to the login screen', async ({ page }) => {
  // addInitScript injects before any page JS runs, so the fake token is in
  // localStorage when useEffect reads it on mount. page.evaluate + page.reload()
  // loses the token because the reload lands on a fresh browser storage context.
  await page.addInitScript(() => {
    localStorage.setItem(
      'token',
      'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmYWtlIn0.invalidsignature',
    );
  });

  // Register before navigation so the GET fired by useEffect on mount is captured.
  const projectsResponsePromise = page.waitForResponse(
    (res) => res.url().includes('/projects/') && res.request().method() === 'GET',
  );

  await page.goto('/');

  // Confirm the backend rejected the invalid token with 401.
  const response = await projectsResponsePromise;
  expect(response.status()).toBe(401);

  // The app must clear the token, return to the login screen, and show the message.
  await expect(page.getByText('Sign In')).toBeVisible();
  await expect(page.getByText('Session expired. Please log in again.')).toBeVisible();

  const token = await page.evaluate(() => localStorage.getItem('token'));
  expect(token).toBeNull();
});
