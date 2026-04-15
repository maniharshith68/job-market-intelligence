#!/bin/bash
set -e

echo "============================================================"
echo "  JOB MARKET INTELLIGENCE PLATFORM — STARTING UP"
echo "============================================================"

echo "[1/2] Waiting for PostgreSQL..."
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

orig_getaddrinfo = socket.getaddrinfo
def getaddrinfo_ipv4(h, p, family=0, type=0, proto=0, flags=0):
    return orig_getaddrinfo(h, p, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = getaddrinfo_ipv4

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

if [ ! -f "data/raw/jobs.csv" ]; then
    echo "ERROR: data/raw/jobs.csv not found!"
    exit 1
fi

echo "[2/2] Checking if pipeline needs to run..."
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
from sqlalchemy import text

engine = get_engine()
needs_pipeline = True

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM job_postings"))
        count = result.scalar()
        if count and count > 0:
            print(f"  DB already has {count} jobs — skipping pipeline ✅")
            needs_pipeline = False
        else:
            print("  DB is empty — pipeline needed")
except Exception as e:
    print(f"  DB check: {str(e)[:100]} — running pipeline")

if needs_pipeline:
    print("[3/5] Running ingestion pipeline...")
    from src.ingestion.run_ingestion import run as run_ingestion
    run_ingestion()
    print("  Ingestion complete ✅")

    print("[4/5] Running NLP + NER pipelines...")
    from src.nlp.run_nlp import run as run_nlp
    run_nlp()
    from src.nlp.run_ner import run as run_ner
    run_ner()
    print("  NLP + NER complete ✅")

    print("[5/5] Loading data into database...")
    from src.database.run_database import run as run_db
    run_db()
    print("  Database loaded ✅")

print("Pipeline check complete — starting dashboard...")
EOF

# REPLACE the last line
echo "============================================================"
echo "  Starting dashboard at http://0.0.0.0:8050"
echo "============================================================"
gunicorn --config gunicorn_config.py "src.dashboard.app:server"
