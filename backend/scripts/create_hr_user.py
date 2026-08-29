"""
Creates (or resets the password for) the single HR Manager account so
there's someone who can log in. Run once after migrations:

    cd backend
    python -m scripts.create_hr_user

Override the default demo credentials with env vars if needed:
    HR_USERNAME=someone HR_PASSWORD=something python -m scripts.create_hr_user
"""
import os

from app.auth import hash_password
from app.database import SessionLocal
from app.models import User

DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "Admin@12345"


def create_hr_user(username=None, password=None):
    username = username or os.environ.get("HR_USERNAME", DEFAULT_USERNAME)
    password = password or os.environ.get("HR_PASSWORD", DEFAULT_PASSWORD)

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            user = User(username=username, password_hash=hash_password(password))
            db.add(user)
            print(f"Created HR user '{username}'")
        else:
            user.password_hash = hash_password(password)
            print(f"Updated password for existing HR user '{username}'")
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    create_hr_user()
