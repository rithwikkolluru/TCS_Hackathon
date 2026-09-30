FROM python:3.11-slim

WORKDIR /app

# Install system build dependencies for scikit-learn, pyarrow, psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency requirements
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy source code, models, data, reports
COPY . .

# Expose FastAPI backend port
EXPOSE 8000

# Run database migration/seed and start uvicorn
CMD ["sh", "-c", "python scripts/seed_database.py && uvicorn backend.app.main:app --host 0.0.0.0 --port 8000"]
