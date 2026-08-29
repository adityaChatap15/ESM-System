# Employee Salary Management System

A web app for ACME's HR Manager to manage salary data for 10,000 employees across
countries, and answer questions about how the org pays its people — replacing
spreadsheet-based tracking.

Full requirements and scope decisions: [`docs/requirements.md`](docs/requirements.md).

## Stack

- **Backend:** FastAPI (Python) + SQLAlchemy + PostgreSQL
- **Frontend:** React (Vite) + shadcn/ui + Recharts
- **Deployment:** Render (backend + Postgres), Vercel (frontend)

## Project layout

```
backend/    FastAPI app, models, migrations, seed script, tests
frontend/   React app
docs/       requirements, architecture, AI-usage notes
```

## Status

This project is being built in phases, each committed separately. Setup, seeding,
testing, and deployment instructions will be filled in here as each phase lands
(see `docs/` for design notes as they're added).
