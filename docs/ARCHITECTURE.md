# Architecture notes

Quick rundown of how this is put together and why I made the calls I made.
Not trying to be exhaustive here, just enough that someone opening this repo
cold can figure out where things live and why.

## The big picture

```
                    +-------------+
                    |   Vercel    |   React (Vite) SPA
                    |  (frontend) |   - login, employee list/detail, analytics
                    +------+------+
                           | HTTPS (REST, JWT bearer)
                    +------v------+
                    |   Render    |   FastAPI app
                    |  (backend)  |   - employees, salary, auth, analytics routers
                    +------+------+
                           | SQLAlchemy
                    +------v------+
                    |   Render    |   PostgreSQL (managed)
                    |  Postgres   |
                    +-------------+
```

Backend on Render, Postgres on Render too (managed), frontend on Vercel as a
static build. Locally I just run a Postgres container instead of the hosted
one (`docker-compose.yml`) and run both apps directly - `uvicorn` for the API,
`npm run dev` for the frontend.

## Data model

Three tables (`backend/app/models.py`):

- `users` - just the one HR manager account, username + bcrypt hash.
- `employees` - name, employee_code, department, role, country, join_date,
  is_active. I put indexes on department/country/role/name since those are
  exactly the columns the search/filter UI hits, and at 10k rows you notice
  the difference.
- `salary_records` - employee_id (FK), amount, currency, effective_date,
  reason.

The one thing worth calling out here: **salary history isn't a column, it's
a table.** Every time a salary changes, that's a new row in `salary_records`,
never an update to an existing one. "Current salary" is just whichever row
has the latest `effective_date` for that employee. This was a deliberate
choice, not something I backed into - an HR manager might log a raise a
month after it actually took effect, so I can't just trust whatever got
inserted last. `get_current_salary()` in `app/salary_logic.py` handles the
lookup, and there's a test in `test_salary.py` that specifically inserts a
later record before an earlier one to make sure the ordering logic doesn't
get lazy and just grab the most recent insert.

Currency isn't something the client sends either - when you record a salary
change, the API looks up the employee's country and derives the currency
from that (`app/constants.py`). That way there's no way to end up with a
salary in the wrong currency for someone's country, which matters a lot
once you get to the analytics side of things (more on that below).

## API

Everything lives under `/api/v1`, and everything except `/auth/login` needs
a bearer token. Rather than checking auth in every single route function, I
just attach the check as a router-level dependency
(`app/auth.py::get_current_user`), so it's enforced once per router instead
of copy-pasted everywhere.

- **auth** - `POST /auth/login`
- **employees** - list (with search/filter/pagination), `GET /employees/filters`
  (distinct department/country/role values currently in the DB - so the
  frontend dropdowns don't hardcode a list that can go stale), get one,
  create, update, delete (soft - flips `is_active`, doesn't touch the row)
- **salary** - get history, add a new record
- **analytics** - summary, distribution, extremes, headcount-payroll

## The currency rule (this is the important part)

The requirements doc rules out FX conversion on purpose - salaries stay in
whatever currency the employee is actually paid in. That sounds like a small
scoping decision but it has real teeth once you get to the analytics
endpoints, because it means **you can never average, sum, or sort salary
amounts across two different currencies.** It's a really easy bug to write by
accident - group by department, run AVG(), done - except if that department
has people in both India and the US you just averaged rupees and dollars
into a number that doesn't mean anything.

So every analytics function in `app/analytics_logic.py` groups by currency
before it does anything else:

- `summary` groups by (dimension, currency) - "average salary by department"
  is really "average salary by department, broken out by currency"
- `distribution` and `extremes` group by currency first too
- `headcount_payroll` groups by country, which happens to map 1:1 to a
  currency anyway, so there's no ambiguity there

Most of `test_analytics.py` exists specifically to make sure this doesn't
regress - there's a test with an India employee and a US employee in the
same department that checks the two currencies come back as separate groups
instead of getting mashed together.

## A few things I did for performance/simplicity reasons

- Employee list is paginated server-side. Never loading all 10k rows into
  the browser and filtering client-side.
- Analytics math (average, median) is done in plain Python
  (`statistics.mean`/`statistics.median`), not with something like Postgres'
  `percentile_cont`. At 10k rows this is fast enough (full-org analytics
  comes back in a bit over a second, checked this manually against the
  seeded data) and it means the same code runs against the in-memory SQLite
  the tests use - no need to spin up Postgres just to run `pytest`. If this
  ever needed to handle millions of rows I'd move the aggregation into SQL,
  but that's not the problem I have right now.
- The seed script uses plain SQLAlchemy (`add_all()` + `flush()`), not some
  hand-rolled bulk insert. SQLAlchemy 2.0 already batches this well against
  Postgres - 10,000 employees plus ~18,600 salary records seed in under 10
  seconds without me doing anything clever.
- Tests don't need Docker running at all. `conftest.py` swaps in an
  in-memory SQLite DB via a FastAPI dependency override, so the whole suite
  runs in under 20 seconds with zero external state.

## Frontend

Plain function components + hooks. No Redux, no state management library.
I'd originally planned on shadcn/ui for components but its CLI kept failing
to detect a perfectly valid Tailwind v3 setup (turned out to be a real bug in
that tool, not my config) - wasn't worth fighting, so I just hand-wrote
Button/Input/Card as small Tailwind components instead. Simpler anyway.

```
src/
  lib/            api.js (fetch wrapper), useApi.js (adds the auth token)
  context/        AuthContext - login state, token in localStorage
  components/     ProtectedRoute, Layout (shared header/nav), ui/*
  pages/          one file per route
```

Routing is React Router's nested layout pattern - `ProtectedRoute` wraps
`Layout`, which wraps the actual pages, so individual pages don't need to
worry about auth checks or repeating the nav bar.
