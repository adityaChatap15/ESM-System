# How I used AI on this

I built this with Claude Code, working directly in the repo rather than
pasting code back and forth from a chat window. Figured I'd write down the
instructions that shaped the build and the more interesting things that came
up, since the assessment specifically asks for this.

## The ground rules I set upfront

Before any code got written, I gave a few instructions that ended up
shaping the whole rest of the build:

- **Keep the Python simple.** No service/repository layers, no clever
  abstractions, no metaclasses or decorator soup - just plain functions and
  direct DB queries where a direct query is all you need. Same idea on the
  frontend: plain React components and hooks, no Redux.
- **Build it in phases, and I handle git myself.** I didn't want the AI
  running `git add`/`commit`/`push` on its own. Every phase had to end with
  a plain explanation of what changed and why, then the exact commands for
  me to run and push myself. That's why the commit history reads as a
  sequence of small, complete steps instead of one giant commit dump.
- **Postgres, not SQLite, and Render + Vercel for hosting.** The assessment
  example used SQLite, but I wanted Postgres since that's closer to what
  I'd actually use, and I picked the deploy targets (Render for the API +
  DB, Vercel for the static frontend) before any code existed.

The requirements doc (`docs/requirements.md`) got written and locked in
before any implementation started, same as the assessment asks - what's in
scope, what's deliberately cut, and why.

## Decisions that came out of the process

- **FastAPI + React** as the stack - matched what I already know from my
  own background (FastAPI/Django/Python backend work, React from a side
  project), rather than picking something unfamiliar just because it's
  trendy.
- **Currency gets derived server-side, not sent by the client.** A salary
  record doesn't take a currency field in the request - it's looked up from
  the employee's country. Didn't want "salary recorded in the wrong
  currency" to even be a state the API could represent.
- **"Current salary" = latest effective_date, not latest insert.** Called
  this out on purpose rather than letting it be an accident of whatever the
  last DB row happens to be, and locked it down with tests before it could
  quietly regress later.
- **Analytics never mixes currencies.** Every aggregate groups by currency
  first. This is the one decision in the whole project I'd call genuinely
  load-bearing - see the architecture notes for why.
- **Dropped shadcn/ui partway through the frontend phase** after its CLI
  wouldn't cooperate with a working Tailwind v3 setup (more on this below).

## Bugs that only showed up because I actually ran the thing

A few real issues only surfaced because each phase got run end-to-end -
curl, pytest, and an actual browser - instead of just eyeballing the code
and assuming it worked:

1. **Seed script silently left `employee_id` as NULL.** The first attempt
   at seeding all 10k employees blew up with a Postgres NOT NULL violation.
   Turned out `build_salary_history()` built the `SalaryRecord` objects
   without ever setting `employee_id` on them. The unit tests hadn't caught
   it because they don't touch a real DB with real constraints. Postgres
   rolled the whole batch back cleanly on failure, fixed the one line, reran
   it - 10,000 employees in about 9 seconds.
2. **Analytics charts had correct data but literally no visible bars.**
   Every number on the page was right (confirmed against the tables further
   down), the SVG for each bar had the correct path and fill color in the
   DOM - but nothing rendered. Turned out to be Recharts' default mount
   animation never finishing in a headless browser. Turning off
   `isAnimationActive` fixed it, and honestly it's the right call anyway for
   a dashboard with this much data - no reason for bars to animate in every
   time you change a filter.
3. **shadcn/ui's CLI couldn't see a valid Tailwind config.** Kept failing
   with "No Tailwind CSS configuration found" against a `tailwind.config.js`
   that was working fine. This is a known mismatch - their newer CLI
   versions expect a Tailwind v4 setup and don't handle v3 gracefully.
   Rather than fighting it, I just wrote the three components I needed by
   hand. Less to maintain anyway.
4. **passlib doesn't work with current bcrypt.** The "standard" way most
   FastAPI tutorials do password hashing (`passlib[bcrypt]`) crashed outright
   - passlib hasn't been updated since 2020 and chokes on newer bcrypt
   releases. Swapped to calling `bcrypt` directly, which turned out to be
   less code anyway.
5. **A couple of local environment quirks, not app bugs** - my machine
   already had a native Postgres on port 5432, so the dev container got
   mapped to 5433 instead; and a different, unrelated Docker project on this
   machine was already squatting on port 8000, so verification during one
   phase happened on 8006 instead. Neither got touched, just routed around.

## What I didn't have AI do

- Recording the actual demo video - that's on me.
- The real account-level deploy work (linking the Render/Vercel dashboards,
  clicking through the actual deploy). The Dockerfile, `render.yaml`, and
  `vercel.json` were all written and tested locally first (built the Docker
  image, ran it against Postgres, confirmed it actually served requests)
  so that part is just clicking a few buttons rather than writing code.
