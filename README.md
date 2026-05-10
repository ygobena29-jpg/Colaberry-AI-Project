# Colaberry AI Project

A full-stack project management platform with JWT authentication, user-scoped project CRUD, and automated tests.

**Stack:** Next.js (TypeScript) · FastAPI (Python) · MongoDB · Docker · Playwright · pytest

---

## Prerequisites

- Python 3.12+
- Node.js 20+
- Docker + Docker Compose
- `openssl` (standard on macOS/Linux; on Windows use Git Bash or WSL)

---

## 1. Generate JWT RSA Keys

The backend signs tokens with an RSA keypair. Run this **once** from the repo root before starting the backend or running any tests:

```bash
openssl genrsa -out secrets/jwt_private_key.pem 2048
openssl rsa -in secrets/jwt_private_key.pem -pubout -out secrets/jwt_public_key.pem
```

Both files must be at `secrets/jwt_private_key.pem` and `secrets/jwt_public_key.pem` relative to the repo root. The `secrets/` directory is already in `.gitignore` — do not commit these files.

---

## 2. Start the Backend

**Option A — Docker (recommended):**

```bash
docker compose up --build
```

Starts FastAPI on `http://localhost:8080` and MongoDB on port 27017. Docker reads the keys from `secrets/` automatically via Docker secrets.

**Option B — without Docker:**

```bash
cd backend
pip install -r requirements.txt
MONGO_URL=mongodb://localhost:27017 \
JWT_PRIVATE_KEY_PATH=../secrets/jwt_private_key.pem \
JWT_PUBLIC_KEY_PATH=../secrets/jwt_public_key.pem \
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

Requires a local MongoDB instance on port 27017.

---

## 3. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

Opens at `http://localhost:3000`. The app talks to the backend at `http://localhost:8080`.

---

## 4. Run Backend Unit Tests

The backend does **not** need to be running — pytest uses an in-process test client.

```bash
cd backend
pytest
```

`backend/tests/conftest.py` automatically sets `JWT_PRIVATE_KEY_PATH` and `JWT_PUBLIC_KEY_PATH` to point at `secrets/*.pem`, so the keys from Step 1 are used.

---

## 5. Run Frontend E2E Tests (Playwright)

**One-time setup — install Chromium:**

```bash
cd frontend
npx playwright install chromium
```

**Prerequisite:** The FastAPI backend must be running on `http://localhost:8080` before E2E tests start (use `docker compose up` or Option B above). Playwright auto-starts the Next.js dev server on port 3000, so you do not need to run `npm run dev` separately.

**Run the tests:**

```bash
cd frontend
npm run test:e2e
```

To open the interactive Playwright UI (useful for debugging):

```bash
cd frontend
npm run test:e2e:ui
```

---

## CI

GitHub Actions runs two jobs on every push and pull request:

1. **`test`** — runs `pytest` against a live MongoDB service container.
2. **`e2e`** — starts the FastAPI backend and runs all 7 Playwright tests (gated on `test` passing).

Both jobs generate a temporary RSA keypair via `openssl` — no secrets are committed to the repository.
