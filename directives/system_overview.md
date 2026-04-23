# System Overview Directive

**Version:** 1.0  
**Status:** Active  
**Last Updated:** 2026-04-23  
**Audience:** All developers, interns, and AI coding agents working in this repository

---

## 1. System Purpose

This system is a project management application.

It allows authenticated users to create, view, update, and delete their own projects through a web interface backed by an API.

The system does not currently include AI workflow automation, client onboarding, reporting, notifications, or external integrations. Any future scope expansion must be added to this directive by a human decision-maker before implementation begins.

---

## 2. Inputs

The system receives the following inputs:

- **User credentials** — an email address and password submitted through the login form
- **Project data** — a project name provided by the user when creating or editing a project
- **Project identifiers** — a unique project ID used to target edit and delete operations
- **Authentication token** — a bearer token issued at login and sent with every protected API request

There are no scheduled jobs, automated triggers, or background processes in the current scope. All actions are initiated manually by a logged-in user through the UI.

---

## 3. Outputs

The system produces the following outputs:

- **Session token** — returned to the frontend after a successful login and stored locally in the browser
- **Project list** — a user-specific list of projects retrieved from the backend and displayed in the UI
- **CRUD operation results** — confirmation or error messages shown to the user after creating, updating, or deleting a project
- **API responses** — structured JSON responses from the backend for all project and authentication operations

The system does not currently produce reports, exports, notifications, or any output intended for third-party systems.

---

## 4. Success Criteria

The system is working correctly when all of the following are true:

- A user can log in with valid credentials and receive a session token
- After login, the user's projects load automatically without a manual refresh
- A user can create a new project and see it appear immediately in the list
- A user can edit a project name and see the updated name immediately in the list
- A user can delete a project after confirming the action, and it is removed from the list
- After logging out, the session token is cleared and the dashboard is no longer visible
- On page refresh, a user with a valid session token remains logged in and their projects reload
- When a token expires or is invalid, the user is automatically returned to the login screen with a clear message

---

## 5. Edge Cases

The following scenarios are known and must be handled gracefully:

- **Expired or invalid token** — the backend returns 401; the frontend must clear the token, reset the logged-in state, and show a message asking the user to log in again
- **User with no projects** — the project list is empty; the UI must display a clear empty state message rather than an error
- **Empty or invalid project fields** — a project name must not be blank; the system must reject or ignore empty submissions
- **Failed network or API request** — if the backend is unreachable, the UI must show a plain-language error message and must not crash or expose raw error details
- **Unauthenticated access attempt** — any request to a protected endpoint without a valid token must be rejected; no project data may be returned
- **Accidental delete** — a confirmation step must precede any delete action so the user cannot delete a project by mistake

---

## 6. Safety Constraints

The following rules must never be violated under any circumstances:

- **User isolation** — a user must never be able to see, edit, or delete another user's projects; all project queries must be scoped to the authenticated user
- **No secrets in the repository** — API keys, passwords, tokens, and credentials must never be committed to version control
- **No production writes without environment checks** — any script or operation that writes data must first confirm it is not targeting a production environment
- **Destructive actions require confirmation** — delete operations must always be preceded by an explicit user confirmation; they must not be triggered automatically or silently
- **Authentication failures must not expose data** — a failed or missing authentication must return an appropriate error response only; it must never return partial or protected data
- **Token storage is client-side only** — session tokens are stored in the browser's localStorage; they must never be logged to persistent server-side storage or included in error responses

---

## How Success Is Verified

This directive is verified through the following methods:

- **Manual testing** — a tester walks through each success criterion in section 4 using a real browser session
- **Automated unit tests** — backend authentication and project CRUD logic must have passing unit tests in `/tests`
- **Automated end-to-end tests** — auth flow, project list loading, CRUD operations, and logout must be covered by browser-based tests (Playwright preferred)
- **Edge case validation** — each scenario in section 5 must have a corresponding test case that confirms the correct behavior
- **Security review** — before any release, confirm no secrets are present in the repository and that user isolation is enforced at the API level

This directive must be updated whenever the system scope changes. It is not optional documentation — it is the source of truth for what this system is and how it must behave.

---

## Verification Mapping

Each success criterion is assigned exactly one verification method. A criterion is not considered done until its assigned verification passes.

| Success Criterion | Verification Method |
|---|---|
| A user can log in with valid credentials and receive a session token | E2E test (Playwright: auth flow — login form submission, token stored in localStorage) |
| After login, the user's projects load automatically without a manual refresh | E2E test (Playwright: auth flow — project list visible immediately after login) |
| A user can create a new project and see it appear immediately in the list | E2E test (Playwright: project CRUD — create project, verify name appears in list) |
| A user can edit a project name and see the updated name immediately in the list | E2E test (Playwright: project CRUD — edit project, verify updated name in list) |
| A user can delete a project after confirming the action, and it is removed from the list | E2E test (Playwright: project CRUD — confirm delete dialog, verify project removed) |
| After logging out, the session token is cleared and the dashboard is no longer visible | E2E test (Playwright: auth flow — logout, verify login form shown, localStorage cleared) |
| On page refresh, a user with a valid session token remains logged in and their projects reload | E2E test (Playwright: auth flow — refresh page, verify dashboard still visible and projects loaded) |
| When a token expires or is invalid, the user is automatically returned to the login screen with a clear message | Unit test (backend: auth middleware rejects expired token with 401) + E2E test (Playwright: simulate 401 response, verify login screen and message appear) |
