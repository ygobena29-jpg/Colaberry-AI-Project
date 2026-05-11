# Delivery Status

**Assessed against:** `directives/system_overview.md` v1.0  
**Assessment date:** 2026-05-10 (updated 2026-05-11, all 8 criteria now verified)  
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
| E2E auth tests (Playwright) | `frontend/tests/auth.spec.ts` — 5 tests (includes dedicated criterion 7 assertion) |
| E2E project CRUD tests (Playwright) | `frontend/tests/projects.spec.ts` — 4 tests (includes dedicated criterion 2 assertion) |

---

## 3. Missing or Incomplete Acceptance Evidence

All 8 directive success criteria now have passing verification. Status per criterion:

| # | Criterion | Required verification | Status |
|---|---|---|---|
| 1 | Login stores session token | Playwright: `auth.spec.ts` ✅ | Done |
| 2 | Projects load automatically after login | Playwright: `projects.spec.ts` — pre-creates project via API, logs in via UI, asserts project name visible without reload ✅ | Done |
| 3 | Create project appears immediately | Playwright: `projects.spec.ts` ✅ | Done |
| 4 | Edit project name updates immediately | Playwright: `projects.spec.ts` ✅ | Done |
| 5 | Delete project with confirmation | Playwright: `projects.spec.ts` ✅ | Done |
| 6 | Logout clears token and shows login screen | Playwright: `auth.spec.ts` ✅ | Done |
| 7 | Refresh keeps user on dashboard | Playwright: `auth.spec.ts` — pre-creates project via API, reloads, asserts dashboard + token + project name still visible ✅ | Done |
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
| E2E browser | Playwright | 2 files | 9 tests | Auth (5) + CRUD (4) — Chromium only |
| Frontend unit | — | — | 0 | No component or hook unit tests |
| Edge case E2E | — | — | 0 | None written |

CI runs both the pytest suite (`test` job) and the 9 Playwright E2E tests (`e2e` job, gated on `test` passing). Latest run: both jobs green.

---

## 5. Local Run / Readiness Gaps

| Gap | Status | Detail |
|---|---|---|
| **Secrets not self-documenting** | Closed | Root `README.md` and `frontend/README.md` now include the exact `openssl genrsa` + `openssl rsa` commands and specify `secrets/` as the target directory. |
| **Playwright browsers not installed** | Closed | Both READMEs now have a one-time-setup step: `npx playwright install chromium`. |
| **E2E tests require manual backend** | Closed | Both READMEs now explicitly state the FastAPI backend must be running on `http://localhost:8080` before E2E tests start, with `docker compose up` as the documented method. |
| **Frontend absent from docker-compose** | Open | Only `api` + `mongodb` are in `docker-compose.yml`. The full stack cannot be started with a single `docker compose up`. Requires a code change, not a docs change. |
| **No one-command test execution** | Closed | `scripts/test` runs `pytest` then `npm run test:e2e` in sequence, fails fast if either suite fails, and prints labelled section headers. Documented in root `README.md` §6. |

---

## 6. Final Delivery Verdict

**Partially Delivered**

The core application — authentication, project CRUD, user isolation, Docker setup, and CI — is working and tested. All 8 directive success criteria have passing E2E verification. The system is demonstrably functional.

What prevents a "Delivered" verdict:
- Three directive §5 edge cases have **no automated coverage** (empty project name, empty list state, network failure message) — these are explicitly required verifications in the directive
- Criterion 8 is Done* — the "Session expired" message is a **known UI bug**: it never renders due to a React batch-update ordering issue, so the criterion's message-visibility half is unverified
- Frontend is absent from `docker-compose.yml` — the full stack cannot start with a single command

---

## 7. Prioritised Next Fixes

Smallest changes that move the verdict to "Delivered":

| Priority | Fix | Effort |
|---|---|---|
| 1 | **Fix "Session expired" UI bug** — move `setProjectStatus(...)` out of `{isLoggedIn && ...}` or render it unconditionally so the message is visible after auto-logout | ~30 min |
| 2 | **Add edge case E2E tests** — empty project name, empty list state, and network-failure error message (directive §5) | ~2 hours |
| 3 | **Add frontend service to docker-compose** — add a `frontend` service using `npm run start` so the full stack starts with a single `docker compose up` | ~30 min |
| 4 | **Verify `secrets/*.pem` are in `.gitignore`** — if not, add them immediately to satisfy the "no secrets in repo" safety constraint | ~5 min |
