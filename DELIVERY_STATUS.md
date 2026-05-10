# Delivery Status

**Assessed against:** `directives/system_overview.md` v1.0  
**Assessment date:** 2026-05-10  
**Verdict:** **Partially Delivered**

---

## 1. Project Objective

A web-based project management platform with secure authentication (JWT), user-scoped CRUD operations on projects, and full-stack test coverage. All scope is defined in `directives/system_overview.md`; no AI workflow automation, notifications, or external integrations are in scope.

---

## 2. Implemented Evidence

| Feature | Evidence |
|---|---|
| User registration & login | `backend/app/auth/routes.py`, `test_auth_register.py`, `test_auth_login.py` |
| JWT issuance (RSA-signed) | `backend/app/security/jwt_tokens.py`, `jwt_keys.py`, `test_auth_me.py` |
| Project create / list / patch / delete | `backend/app/projects/routes.py`, `test_projects_create_list.py`, `test_projects_patch.py`, `test_projects_delete.py` |
| User isolation | `routes.py` scopes all queries to `owner_id = current_user["sub"]` |
| Soft delete with list exclusion | `status: "deleted"` pattern; list route filters `{"status": {"$ne": "deleted"}}` |
| Delete confirmation dialog | `deleteProject()` calls `confirm(...)` before DELETE; E2E test verifies |
| Session persistence on refresh | `useEffect` in `page.tsx` reads localStorage token on mount |
| Auto-logout on 401 | `getProjects()` clears token and calls `setIsLoggedIn(false)` on 401 |
| RBAC (admin vs. user) | `test_auth_admin_rbac.py`, `test_auth_admin_access.py` |
| Docker backend + MongoDB | `backend/Dockerfile`, `docker-compose.yml` |
| CI (backend unit tests) | `.github/workflows/ci.yml` runs `pytest` on push/PR |
| E2E auth tests (Playwright) | `frontend/tests/auth.spec.ts` — 3 tests |
| E2E project CRUD tests (Playwright) | `frontend/tests/projects.spec.ts` — 3 tests |

---

## 3. Missing or Incomplete Acceptance Evidence

The directive's Verification Mapping requires a passing test for each of its 8 success criteria. Status per criterion:

| # | Criterion | Required verification | Status |
|---|---|---|---|
| 1 | Login stores session token | Playwright: `auth.spec.ts` ✅ | Done |
| 2 | Projects load automatically after login | Playwright: no standalone test; implicitly covered by edit/delete setup assertions | **Gap** |
| 3 | Create project appears immediately | Playwright: `projects.spec.ts` ✅ | Done |
| 4 | Edit project name updates immediately | Playwright: `projects.spec.ts` ✅ | Done |
| 5 | Delete project with confirmation | Playwright: `projects.spec.ts` ✅ | Done |
| 6 | Logout clears token and shows login screen | Playwright: `auth.spec.ts` ✅ | Done |
| 7 | Refresh keeps user on dashboard | Playwright: `auth.spec.ts` checks heading + token, but does not assert that project *data* reloaded | **Gap** |
| 8 | Expired/invalid token → login screen + message | **No E2E test exists** | **Missing** |

**Edge case tests (directive §5) — all missing from E2E:**

- Empty project name is rejected without a crash
- Empty project list shows the "No projects yet" state (not an error)
- Network failure shows a plain-language message and does not crash
- Unauthenticated request to `/projects/` is rejected (covered by backend middleware, no E2E)

---

## 4. Test Coverage Summary

| Layer | Framework | Files | Tests | Notes |
|---|---|---|---|---|
| Backend unit | pytest | 9 files | ~11 tests | Auth + full CRUD + RBAC — all passing in CI |
| E2E browser | Playwright | 2 files | 6 tests | Auth (3) + CRUD (3) — Chromium only |
| Frontend unit | — | — | 0 | No component or hook unit tests |
| Edge case E2E | — | — | 0 | None written |

CI runs **only** the pytest suite. The 6 Playwright tests are not wired into CI.

---

## 5. Local Run / Readiness Gaps

| Gap | Detail |
|---|---|
| **Secrets not self-documenting** | `secrets/jwt_private_key.pem` and `secrets/jwt_public_key.pem` must exist before the backend or tests can start. No `README` step, `Makefile`, or generation script guides a new developer to create them. CI generates them via `openssl` — the same step is not documented locally. |
| **Playwright browsers not installed** | `npx playwright install chromium` must be run once before `npm run test:e2e`. This step is missing from the README setup instructions. |
| **Frontend absent from docker-compose** | Only `api` + `mongodb` are in `docker-compose.yml`. The full stack cannot be started with a single `docker compose up`. |
| **E2E tests require manual backend** | `playwright.config.ts` uses `webServer` to auto-start Next.js, but the FastAPI backend must be started separately. This is not documented clearly in the README. |
| **No one-command test execution** | The directive requires "one-command test execution must exist." Backend tests: `cd backend && pytest`. E2E tests: `cd frontend && npm run test:e2e`. No top-level `Makefile` or script ties them together. |

---

## 6. Final Delivery Verdict

**Partially Delivered**

The core application — authentication, project CRUD, user isolation, Docker setup, and CI — is working and tested. Six of eight directive success criteria have passing verification. The system is demonstrably functional.

What prevents a "Delivered" verdict:
- Criterion 8 (expired token flow) has **no test at all**
- E2E tests are **not in CI**, so they do not gate any release
- Three directive edge cases have **no automated coverage**
- Local setup has **undocumented dependencies** that would block a new developer

---

## 7. Prioritised Next Fixes

Smallest changes that move the verdict to "Delivered":

| Priority | Fix | Effort |
|---|---|---|
| 1 | **Add E2E test for expired/invalid token** — inject a bad token into localStorage, reload, assert login screen appears with the "Session expired" message | ~1 hour |
| 2 | **Add Playwright run to CI** — add a job to `.github/workflows/ci.yml` that installs browsers and runs `npm run test:e2e` against a live backend service | ~1 hour |
| 3 | **Document local secrets generation** — add an `openssl genrsa` step to the README (mirrors what CI already does) | ~15 min |
| 4 | **Document `npx playwright install chromium`** — one line in the README setup section | ~5 min |
| 5 | **Add dedicated E2E assertion: projects load after login** — in `auth.spec.ts`, pre-create a project and assert its name is visible after login without a reload | ~30 min |
| 6 | **Add frontend service to docker-compose** — add a `frontend` service using `npm run start` (requires a separate build step or dev mode) | ~30 min |
| 7 | **Add edge case E2E tests** — empty project name, empty list state, and the 401-on-project-fetch path | ~2 hours |
| 8 | **Verify `secrets/*.pem` are in `.gitignore`** — if not, add them immediately to satisfy the "no secrets in repo" safety constraint | ~5 min |
