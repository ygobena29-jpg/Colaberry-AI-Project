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

test('invalid token is cleared and user is returned to the login screen', async ({ page }) => {
  // Register the /projects/ listener before the reload so we don't miss
  // the GET request that useEffect fires on mount.
  const projectsResponsePromise = page.waitForResponse(
    (res) => res.url().includes('/projects/') && res.request().method() === 'GET',
  );

  // Inject a syntactically valid but cryptographically invalid JWT.
  // The backend's RS256 verifier will reject it and return 401.
  await page.evaluate(() => {
    localStorage.setItem(
      'token',
      'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmYWtlIn0.invalidsignature',
    );
  });

  // Reload so useEffect reads the fake token and calls getProjects().
  await page.reload();

  // Confirm the backend rejected the token.
  const response = await projectsResponsePromise;
  expect(response.status()).toBe(401);

  // The app must return to the login screen.
  await expect(page.getByText('Sign In')).toBeVisible();

  // NOTE: The app calls setProjectStatus("Session expired. Please log in again.")
  // but that text lives inside {isLoggedIn && (...)} which is unmounted when
  // setIsLoggedIn(false) fires in the same React batch — so it is never rendered.
  // This is a known UI gap documented in DELIVERY_STATUS.md.

  // The invalid token must have been removed from localStorage.
  const token = await page.evaluate(() => localStorage.getItem('token'));
  expect(token).toBeNull();
});
