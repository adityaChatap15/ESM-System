FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render (and most PaaS) inject PORT at runtime; 8000 is the local-dev fallback.
EXPOSE 8000

# Run pending migrations, then start the API. Shell form so $PORT expands.
CMD alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
