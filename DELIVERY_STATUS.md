# Delivery Status

**Assessed against:** `directives/system_overview.md` v1.0  
**Assessment date:** 2026-05-10 (updated 2026-05-10, README docs pass)  
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
| CI (backend unit tests + Playwright E2E) | `.github/workflows/ci.yml` — `test` job runs `pytest`; `e2e` job starts backend and runs Playwright on push/PR |
| E2E auth tests (Playwright) | `frontend/tests/auth.spec.ts` — 4 tests |
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
| 8 | Expired/invalid token → login screen + message | Playwright: `auth.spec.ts` — injects invalid JWT, reloads, asserts 401 from backend, verifies login screen and token removal ✅ | Done* |

**Note on criterion 8 (\*):** The `getProjects` 401 handler calls `setProjectStatus("Session expired. Please log in again.")`, but that `<p>` element is inside `{isLoggedIn && (...)}`. Because `setIsLoggedIn(false)` fires in the same React batch, the section unmounts before the message renders. The E2E test asserts the login screen appears and the token is cleared — it does not assert the message text, which is a known UI bug.

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
| E2E browser | Playwright | 2 files | 7 tests | Auth (4) + CRUD (3) — Chromium only |
| Frontend unit | — | — | 0 | No component or hook unit tests |
| Edge case E2E | — | — | 0 | None written |

CI runs both the pytest suite (`test` job) and the 7 Playwright E2E tests (`e2e` job, gated on `test` passing). Latest run: both jobs green.

---

## 5. Local Run / Readiness Gaps

| Gap | Status | Detail |
|---|---|---|
| **Secrets not self-documenting** | Closed | Root `README.md` and `frontend/README.md` now include the exact `openssl genrsa` + `openssl rsa` commands and specify `secrets/` as the target directory. |
| **Playwright browsers not installed** | Closed | Both READMEs now have a one-time-setup step: `npx playwright install chromium`. |
| **E2E tests require manual backend** | Closed | Both READMEs now explicitly state the FastAPI backend must be running on `http://localhost:8080` before E2E tests start, with `docker compose up` as the documented method. |
| **Frontend absent from docker-compose** | Open | Only `api` + `mongodb` are in `docker-compose.yml`. The full stack cannot be started with a single `docker compose up`. Requires a code change, not a docs change. |
| **No one-command test execution** | Open | Backend tests (`cd backend && pytest`) and E2E tests (`cd frontend && npm run test:e2e`) are now documented separately. No top-level `Makefile` or script unifies them. The CLAUDE.md intern-safety rule requires a single command. |

---

## 6. Final Delivery Verdict

**Partially Delivered**

The core application — authentication, project CRUD, user isolation, Docker setup, and CI — is working and tested. Six of eight directive success criteria have passing verification. The system is demonstrably functional.

What prevents a "Delivered" verdict:
- Criteria 2 and 7 have no dedicated assertions (projects load after login; project *data* reloads on refresh)
- Three directive §5 edge cases have **no automated coverage** (empty name, empty list, network failure)
- The "Session expired" message is a **known UI bug**: it never renders due to a React batch-update ordering issue
- Local setup docs are now complete for key generation, Playwright install, and backend startup; but **no single command runs both test suites** (CLAUDE.md intern-safety rule not yet met)

---

## 7. Prioritised Next Fixes

Smallest changes that move the verdict to "Delivered":

| Priority | Fix | Effort |
|---|---|---|
| 1 | **Fix "Session expired" UI bug** — move `setProjectStatus(...)` out of `{isLoggedIn && ...}` or render it unconditionally so the message is visible after auto-logout | ~30 min |
| 2 | **Add top-level one-command test runner** — add a `Makefile` or shell script at repo root that runs `cd backend && pytest` then `cd frontend && npm run test:e2e` (satisfies CLAUDE.md intern-safety rule) | ~15 min |
| 3 | **Add dedicated E2E assertion: projects load after login** — in `auth.spec.ts`, pre-create a project and assert its name is visible after login without a reload (criterion 2) | ~30 min |
| 4 | **Add dedicated E2E assertion: project data reloads on refresh** — extend the refresh test to assert at least one project name is visible after reload (criterion 7) | ~15 min |
| 5 | **Add frontend service to docker-compose** — add a `frontend` service using `npm run start` so the full stack starts with a single `docker compose up` | ~30 min |
| 6 | **Add edge case E2E tests** — empty project name, empty list state, and network-failure error message (directive §5) | ~2 hours |
| 7 | **Verify `secrets/*.pem` are in `.gitignore`** — if not, add them immediately to satisfy the "no secrets in repo" safety constraint | ~5 min |
