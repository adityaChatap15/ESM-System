"""
Plain settings module. Values come from environment variables, with sensible
local-dev defaults so the app can run without any setup.
"""
import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://esm_user:esm_password@localhost:5433/esm_db",
)

JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.environ.get("JWT_EXPIRE_MINUTES", "60"))
