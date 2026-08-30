# Employee Salary Management System

A web app for ACME's HR Manager to manage salary data for 10,000 employees across
countries, and answer questions about how the org pays its people — replacing
spreadsheet-based tracking.

- Requirements and scope decisions: [`docs/requirements.md`](docs/requirements.md)
- System design and key decisions: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- How AI was used to build this: [`docs/AI_PROMPTS.md`](docs/AI_PROMPTS.md)

## Stack

- **Backend:** FastAPI (Python) + SQLAlchemy + PostgreSQL
- **Frontend:** React (Vite) + Tailwind CSS + Recharts
- **Deployment:** Render (backend + Postgres), Vercel (frontend)

## Project layout

```
backend/    FastAPI app, models, migrations, seed script, tests
frontend/   React app
docs/       requirements, architecture, AI-usage notes
```

## Prerequisites

- Python 3.13+
- Node 22+
- Docker (for a local Postgres container)

## Backend setup

```bash
cd backend
python -m venv .venv

# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements-dev.txt   # includes requirements.txt + pytest/httpx
cp .env.example .env
```

Start local Postgres (from the repo root) and apply migrations:

```bash
docker compose up -d
cd backend
alembic upgrade head
```

> The Postgres container is mapped to **port 5433**, not 5432 - this avoids
> clashing with a native Postgres install some machines already have running
> on 5432. `.env.example` already points at 5433.

Create the seeded HR Manager login, then run the API:

```bash
python -m scripts.create_hr_user
uvicorn app.main:app --reload
```

Backend is now at `http://localhost:8000` (docs at `/docs`). Demo login:
**username `admin`, password `Admin@12345`** (change via `HR_USERNAME`/
`HR_PASSWORD` env vars before running the script, if you want different
credentials).

### Seed 10,000 employees

```bash
cd backend
python -m scripts.seed
```

Generates ~10,000 employees across 10 countries, 8 departments, and 40 roles,
each with 1-3 salary records (hire + raises). Safe to re-run - it skips if the
`employees` table already has rows. Takes under 10 seconds.

### Run tests

```bash
cd backend
pytest
```

37 tests, all against an in-memory SQLite database (no Docker/Postgres
required to run them) - fast and deterministic.

## Frontend setup

```bash
cd frontend
npm install
cp .env.example .env   # points VITE_API_BASE_URL at your local backend
npm run dev
```

Frontend is now at `http://localhost:5173`.

## Deployment

Backend deploys to **Render** (Docker web service + managed Postgres),
frontend to **Vercel** (static build). Deploy in this order, since each side
needs to know the other's URL:

1. **Backend on Render:** Render dashboard -> New -> Blueprint -> point at
   this repo (`render.yaml` at the repo root defines both the web service and
   the Postgres database). Render generates `DATABASE_URL` and
   `JWT_SECRET_KEY` automatically.
2. Once live, run the one-time setup against the production database (Render
   dashboard -> your service -> Shell):
   ```bash
   python -m scripts.create_hr_user
   python -m scripts.seed
   ```
3. **Frontend on Vercel:** import this repo, set the project's **Root
   Directory** to `frontend`, and set the env var `VITE_API_BASE_URL` to the
   Render backend's URL from step 1. Vercel auto-detects the Vite build;
   `frontend/vercel.json` handles SPA routing so direct links like
   `/employees/5` don't 404.
4. **Close the loop:** update the backend's `CORS_ALLOWED_ORIGINS` env var
   (Render dashboard) to the Vercel URL from step 3, replacing the default
   `*`.

## Demo credentials

- Username: `admin`
- Password: `Admin@12345`

(Seeded by `scripts/create_hr_user.py` - override with `HR_USERNAME`/
`HR_PASSWORD` env vars if you need different credentials, e.g. in production.)
