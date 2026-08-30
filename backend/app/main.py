"""
FastAPI app entry point. Routers get added here as each phase builds them
(employees, salary, auth, analytics).
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ALLOWED_ORIGINS
from app.routers import analytics, auth, employees, salary

app = FastAPI(title="Employee Salary Management System")

app.include_router(auth.router)
app.include_router(employees.router)
app.include_router(salary.router)
app.include_router(analytics.router)

# "*" for local dev; set CORS_ALLOWED_ORIGINS to the real frontend URL(s)
# (comma-separated) in production.
allowed_origins = ["*"] if CORS_ALLOWED_ORIGINS == "*" else CORS_ALLOWED_ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}
