#!/bin/bash
set -e

echo "============================================================"
echo "  JOB MARKET INTELLIGENCE PLATFORM — STARTING UP"
echo "============================================================"

echo "[1/3] Waiting for PostgreSQL..."
python - <<EOF
import time
import psycopg2
import os
import socket

host = os.environ.get("POSTGRES_HOST", "db")
port = int(os.environ.get("POSTGRES_PORT", 5432))
db = os.environ.get("POSTGRES_DB", "jobmarket")
user = os.environ.get("POSTGRES_USER", "admin")
password = os.environ.get("POSTGRES_PASSWORD", "admin123")
app_env = os.environ.get("APP_ENV", "development")

extra = {"sslmode": "require"} if (
    app_env == "production" or
    "supabase" in host or
    "pooler" in host
) else {}

# Force IPv4 — required for Render free tier
orig = socket.getaddrinfo
def ipv4(h, p, family=0, type=0, proto=0, flags=0):
    return orig(h, p, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = ipv4

for i in range(60):
    try:
        conn = psycopg2.connect(
            host=host, port=port, dbname=db,
            user=user, password=password,
            connect_timeout=30,
            **extra
        )
        conn.close()
        print("  PostgreSQL is ready ✅")
        break
    except psycopg2.OperationalError as e:
        print(f"  Retrying in 3s... ({i+1}/60) — {str(e)[:80]}")
        time.sleep(3)
else:
    print("ERROR: PostgreSQL did not become ready in time.")
    exit(1)
EOF

echo "[2/3] Loading data into database..."
python - <<EOF
import os
import sys
import socket

# Force IPv4
orig = socket.getaddrinfo
def ipv4(h, p, family=0, type=0, proto=0, flags=0):
    return orig(h, p, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = ipv4

sys.path.insert(0, '/app')
os.environ.setdefault('APP_ENV', 'production')

from src.database.connection import get_engine, test_connection
from src.database.models import Base
from sqlalchemy import text

engine = get_engine()

# Always create tables first
Base.metadata.create_all(engine)
print("  Tables created/verified ✅")

# Check if data already loaded
try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM job_postings"))
        count = result.scalar()
        if count and count > 0:
            print(f"  DB already has {count} jobs — skipping insert ✅")
            exit(0)
except Exception as e:
    print(f"  DB check error: {e}")

# Load data from pre-built CSVs
print("  Inserting data from pre-built CSVs...")
from src.database.run_database import run as run_db
run_db()
print("  Database loaded ✅")
EOF

echo "[3/3] Starting dashboard..."
echo "============================================================"
python -m src.dashboard.app
