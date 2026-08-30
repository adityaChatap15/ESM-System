# Frontend

React (Vite) app for the Employee Salary Management System HR Manager UI.

## Setup

```bash
npm install
cp .env.example .env   # point VITE_API_BASE_URL at your running backend
npm run dev
```

## Structure

```
src/
  lib/api.js            plain fetch wrapper (talks to the FastAPI backend)
  context/AuthContext.jsx  login/logout state, JWT stored in localStorage
  components/ui/         small hand-written Tailwind components (Button, Input, Card)
  components/ProtectedRoute.jsx  redirects to /login if not authenticated
  pages/                 one file per route
```
