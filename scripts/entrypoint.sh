#!/bin/bash
set -e

echo "============================================================"
echo "  JOB MARKET INTELLIGENCE PLATFORM — STARTING UP"
echo "============================================================"

echo "[1/5] Waiting for PostgreSQL..."
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

extra = {"sslmode": "require"} if (app_env == "production" or "supabase" in host or "pooler" in host) else {}

# Force IPv4 only
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

echo "[2/5] Running data ingestion pipeline..."
python -m src.ingestion.run_ingestion
echo "  Ingestion complete ✅"

echo "[3/5] Running NLP pipeline..."
python -m src.nlp.run_nlp
echo "  NLP pipeline complete ✅"

echo "[4/5] Running NER skill extraction..."
python -m src.nlp.run_ner
echo "  NER complete ✅"

echo "[5/5] Loading data into PostgreSQL..."
python -m src.database.run_database
echo "  Database loaded ✅"

echo "============================================================"
echo "  Starting dashboard at http://0.0.0.0:8050"
echo "============================================================"
python -m src.dashboard.app
