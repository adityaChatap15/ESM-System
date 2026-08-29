"""
FastAPI app entry point. Routers get added here as each phase builds them
(employees, salary, auth, analytics).
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Employee Salary Management System")

# Wide open for local development; tightened to the real frontend origin
# when we wire up deployment (Phase 12).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}
