import { test, expect } from '@playwright/test';

const API_URL       = process.env.API_URL       ?? 'http://localhost:8080';
// Use a unique email per run so there are no password-collision issues.
const TEST_EMAIL    = process.env.TEST_EMAIL    ?? `projects-${Date.now()}@example.com`;
const TEST_PASSWORD = process.env.TEST_PASSWORD ?? 'Test1234!';

// Acquired in beforeAll; used for direct API calls inside tests (project setup).
let authToken: string;

// ── Setup ────────────────────────────────────────────────────────────────────

test.beforeAll(async ({ request }) => {
  // Register the test user (409 = already exists — that is fine).
  const regRes = await request.post(`${API_URL}/auth/register`, {
    data: { email: TEST_EMAIL, password: TEST_PASSWORD },
  });
  console.log('[beforeAll] register status:', regRes.status(), 'email:', TEST_EMAIL);
  expect([200, 201, 409]).toContain(regRes.status());

  // Login via API once to get a token for direct API calls in test setup.
  const loginRes = await request.post(`${API_URL}/auth/login`, {
    data: { email: TEST_EMAIL, password: TEST_PASSWORD },
  });
  expect(loginRes.ok()).toBeTruthy();
  const body = await loginRes.json();
  authToken = body.access_token;
  console.log('[beforeAll] auth token acquired');
});

// Start every test in a clean logged-out state.
test.beforeEach(async ({ page }) => {
  await page.goto('/');
  await page.evaluate(() => localStorage.clear());
  await page.reload();
});

// ── Helper: log in via the UI and wait for the dashboard ─────────────────────

async function login(page: import('@playwright/test').Page) {
  const responsePromise = page.waitForResponse(
    (res) => res.url().includes('/auth/login') && res.request().method() === 'POST',
  );

  await page.fill('input[type="email"]', TEST_EMAIL);
  await page.fill('input[type="password"]', TEST_PASSWORD);
  await page.click('button:has-text("Login")');

  const loginResponse = await responsePromise;
  const loginBody = await loginResponse.json().catch(() => null);
  console.log('[login] status:', loginResponse.status(), 'body:', loginBody);

  await expect(page.getByText('Projects', { exact: true })).toBeVisible();
}

// ── Project CRUD tests ────────────────────────────────────────────────────────

// Criterion 2: projects load automatically after login (no manual refresh needed).
test('projects created before login are visible immediately after login', async ({ page, request }) => {
  // Pre-create a known project via the API so it exists when the user logs in.
  const projectName = `E2E AutoLoad ${Date.now()}`;
  const createRes = await request.post(`${API_URL}/projects/`, {
    headers: { Authorization: `Bearer ${authToken}` },
    data: { name: projectName, description: '', tags: [] },
  });
  expect(createRes.ok()).toBeTruthy();

  // Register the projects-fetch listener BEFORE login() is called.
  // handleLogin calls setIsLoggedIn(true) then immediately awaits getProjects(),
  // so the GET /projects/ fires before React re-renders the dashboard — if we
  // register after login() the request is already gone.
  const projectsResponsePromise = page.waitForResponse(
    (res) => res.url().includes('/projects/') && res.request().method() === 'GET',
  );

  // Log in via the UI — handleLogin fetches projects automatically on success.
  await login(page);

  // Confirm the automatic fetch succeeded (guards against a silent 200-but-empty response).
  const projectsResponse = await projectsResponsePromise;
  expect(projectsResponse.status()).toBe(200);

  // The pre-created project must be visible without any reload or "Refresh" click.
  await expect(page.getByText(projectName)).toBeVisible();
});

test('create project appears in list immediately', async ({ page }) => {
  await login(page);

  const projectName = `E2E Create ${Date.now()}`;

  // Wire up the response listener and dialog handler BEFORE clicking so neither is missed.
  const createResponsePromise = page.waitForResponse(
    (res) => res.url().includes('/projects/') && res.request().method() === 'POST',
  );
  page.once('dialog', (dialog) => dialog.accept(projectName));

  await page.click('button:has-text("+ Create Project")');
  await createResponsePromise;

  // The new project must appear in the list without a manual refresh.
  await expect(page.getByText(projectName)).toBeVisible();
});

test('edit project name updates in the list', async ({ page, request }) => {
  // Pre-create the project via API so this test does not depend on the create UI.
  const originalName = `E2E Edit ${Date.now()}`;
  const createRes = await request.post(`${API_URL}/projects/`, {
    headers: { Authorization: `Bearer ${authToken}` },
    data: { name: originalName, description: '', tags: [] },
  });
  expect(createRes.ok()).toBeTruthy();

  // Log in via UI — projects load automatically after login.
  await login(page);
  await expect(page.getByText(originalName)).toBeVisible();

  const updatedName = `E2E Updated ${Date.now()}`;

  const patchResponsePromise = page.waitForResponse(
    (res) => res.url().includes('/projects/') && res.request().method() === 'PATCH',
  );
  page.once('dialog', (dialog) => dialog.accept(updatedName));

  // Scope the Edit click to the row that contains the original project name.
  // getByText(originalName) → <span>, .locator('..') → projectRow <div>
  await page
    .getByText(originalName)
    .locator('..')
    .getByRole('button', { name: 'Edit' })
    .click();
  await patchResponsePromise;

  await expect(page.getByText(updatedName)).toBeVisible();
  await expect(page.getByText(originalName)).not.toBeVisible();
});

test('delete project removes it from the list after confirmation', async ({ page, request }) => {
  // Pre-create the project via API.
  const projectName = `E2E Delete ${Date.now()}`;
  const createRes = await request.post(`${API_URL}/projects/`, {
    headers: { Authorization: `Bearer ${authToken}` },
    data: { name: projectName, description: '', tags: [] },
  });
  expect(createRes.ok()).toBeTruthy();

  await login(page);
  await expect(page.getByText(projectName)).toBeVisible();

  const deleteResponsePromise = page.waitForResponse(
    (res) => res.url().includes('/projects/') && res.request().method() === 'DELETE',
  );
  // Accept the confirm("Delete project …?") dialog.
  page.once('dialog', (dialog) => dialog.accept());

  // Scope the Delete click to the correct project row.
  await page
    .getByText(projectName)
    .locator('..')
    .getByRole('button', { name: 'Delete' })
    .click();
  await deleteResponsePromise;

  // The project must no longer be visible anywhere on the page.
  await expect(page.getByText(projectName)).not.toBeVisible();
});
