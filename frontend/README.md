This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.

# 🚀 AI Project Governance Platform

## 📌 Overview
This is a full-stack project management platform designed to help organizations manage AI projects in a centralized and structured way.

Many teams rely on scattered tools like spreadsheets, emails, and notes, which leads to inefficiency and poor visibility. This platform solves that by providing a unified dashboard with authentication, project tracking, and CRUD operations.

---

## 🧠 Problem Statement
Organizations struggle to manage AI projects due to:
- Lack of centralized tracking
- Poor visibility of project status
- Inefficient communication across tools

---

## 💡 Solution
Built a centralized web application that:
- Provides secure authentication
- Allows users to create, update, and manage projects
- Displays project data in a clean dashboard
- Ensures better visibility and control

---

## 🛠️ Tech Stack

### Frontend
- Next.js (React)
- TypeScript

### Backend
- FastAPI (Python)
- MongoDB

### DevOps
- Docker (containerized backend)

---

## 🔑 Features

- 🔐 User Authentication (Login system)
- 📊 Dashboard UI
- ➕ Create Project
- ✏️ Update Project
- ❌ Delete Project
- 🔄 Auto-login (session persistence)
- 🐳 Dockerized backend

---

## ⚙️ How to Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/Colaberry-AI-Project.git
cd Colaberry-AI-Project
```

---

## ✅ Automated Testing (Playwright)

End-to-end tests are written with [Playwright](https://playwright.dev) and cover the full user journey from authentication through project management.

### Verified Flows

**Authentication**
- Login stores JWT token in `localStorage`
- Logout clears the token and returns to the login screen
- Session persists across page refresh

**Project CRUD**
- Create project — appears in the list immediately without a page refresh
- Edit project name — updated name is reflected in the list
- Delete project — confirmation dialog shown; project removed on confirm

### Run the Tests

Start the backend first, then run from the `frontend` folder:

```bash
cd frontend
npm run test:e2e
```

To run with the interactive Playwright UI (useful for debugging):

```bash
npm run test:e2e:ui
```
## ✅ Automated Testing (Playwright)

End-to-end tests are written with Playwright and cover the full user journey from authentication through project management.

### Verified Flows

#### Authentication
- Login stores JWT token in localStorage
- Logout clears the token and returns to the login screen
- Session persists across page refresh

#### Project CRUD
- Create project — appears in the list immediately without a page refresh
- Edit project name — updated name is reflected in the list
- Delete project — confirmation dialog shown; project removed on confirm

### Run the Tests

Start the backend first, then run from the frontend folder:

```bash
cd frontend
npm run test:e2e
