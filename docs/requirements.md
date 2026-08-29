# Requirements Document — Employee Salary Management System

## Goal
Build a web-based salary management system that lets ACME's HR Manager replace error-prone, spreadsheet-based salary tracking for 10,000 employees across multiple countries, and answer questions about how the organization pays its people.

## User Persona
**HR Manager** — needs to view, update, and analyze employee salary data quickly, without touching Excel or writing formulas.

## Scope — In

- **Employee management (CRUD):** Add, view, edit, and deactivate employee records (name, employee ID, department, role, country, join date).
- **Salary management:** View and update current salary per employee, with currency tied to the employee's country.
- **Salary history:** Every salary change is recorded with an effective date and reason (e.g., raise, promotion), so the HR Manager can see how pay evolved over time — not just the current number.
- **Search & filter:** Find employees by name, department, country, or role; filter salary data by these same dimensions.
- **Pay insights / analytics:** Answer common HR questions directly in the UI, e.g.:
  - Average / median salary by country, department, or role
  - Salary distribution (pay bands) across the org
  - Highest/lowest paid employees within a filter
  - Headcount and total payroll cost by country
- **Role-based access (minimal):** Single HR Manager role with authenticated login. No public or employee self-service access in this version.
- **Seed data:** A seed script generating ~10,000 realistic employee + salary records across multiple countries, departments, and roles, to validate the system at real-world scale.

## Scope — Out (and why)

- **Payroll processing & tax calculation** — Left out. Tax rules, deductions, and statutory compliance vary significantly by country and are a specialized domain on their own; building this correctly within the assessment timeframe would compromise quality elsewhere. The system manages salary *data*, not payroll *execution*.
- **Employee self-service portal** — Left out. The persona for this exercise is the HR Manager only; a separate employee-facing login adds auth complexity without serving the stated user.
- **Multi-currency conversion / FX rates** — Left out. Salaries are stored and displayed in the employee's local currency; cross-country totals are shown as counts/aggregates per currency rather than converted into a single currency, avoiding the need for live or assumed FX rates.
- **Org hierarchy / approval workflows** (e.g., manager approves a raise before it applies) — Left out. Out of scope for a first version focused on data management and visibility; can be layered on later.
- **Bulk import/export (CSV upload)** — Considered but left out of the core build to keep scope tight; the seed script covers the "bulk data" need for this assessment. Flagged as a natural next feature.

## Technical Approach (Summary)
- **Backend:** REST API (FastAPI, Python) over a relational database (PostgreSQL), covering employee CRUD, salary CRUD/history, and aggregate query endpoints for the analytics views.
- **Frontend:** React-based UI with a searchable/filterable employee table, an employee detail + salary-history view, and a simple analytics dashboard.
- **Testing:** Unit tests on core logic — salary calculations, aggregate queries, validation rules — kept fast and deterministic.
- **Deployment:** Backend on Render (with Render Postgres), frontend on Vercel, plus a short demo video showing employee management and the "answer questions about pay" analytics flow.

## Success Criteria
The HR Manager can, without touching a spreadsheet: look up any employee's current and historical salary, update pay records safely, and get a straight answer to "how does the org pay people?" broken down by country, department, or role.
