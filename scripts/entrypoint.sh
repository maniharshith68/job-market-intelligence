#!/bin/bash
# scripts/entrypoint.sh

set -e

echo "============================================================"
echo "  JOB MARKET INTELLIGENCE PLATFORM — STARTING UP"
echo "============================================================"

# ── Wait for PostgreSQL using Python ────────────────────────
echo "[1/5] Waiting for PostgreSQL..."
python - <<EOF
import time
import psycopg2
import os

host = os.environ.get("POSTGRES_HOST", "db")
port = int(os.environ.get("POSTGRES_PORT", 5432))
db = os.environ.get("POSTGRES_DB", "jobmarket")
user = os.environ.get("POSTGRES_USER", "admin")
password = os.environ.get("POSTGRES_PASSWORD", "admin123")
app_env = os.environ.get("APP_ENV", "development")

# Use SSL for Supabase
extra = {"sslmode": "require"} if (app_env == "production" or "supabase" in host) else {}

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

# ── Check if data/raw/jobs.csv exists ───────────────────────
if [ ! -f "data/raw/jobs.csv" ]; then
    echo "ERROR: data/raw/jobs.csv not found!"
    exit 1
fi

# ── Run ingestion pipeline ───────────────────────────────────
echo "[2/5] Running data ingestion pipeline..."
python -m src.ingestion.run_ingestion
echo "  Ingestion complete ✅"

# ── Run NLP pipeline ────────────────────────────────────────
echo "[3/5] Running NLP pipeline..."
python -m src.nlp.run_nlp
echo "  NLP pipeline complete ✅"

# ── Run NER pipeline ─────────────────────────────────────────
echo "[4/5] Running NER skill extraction..."
python -m src.nlp.run_ner
echo "  NER complete ✅"

# ── Run database pipeline ────────────────────────────────────
echo "[5/5] Loading data into PostgreSQL..."
python -m src.database.run_database
echo "  Database loaded ✅"

# ── Start dashboard ──────────────────────────────────────────
echo "============================================================"
echo "  Starting dashboard at http://0.0.0.0:8050"
echo "============================================================"
python -m src.dashboard.app
