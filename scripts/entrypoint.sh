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

for i in range(30):
    try:
        conn = psycopg2.connect(
            host=host, port=port, dbname=db,
            user=user, password=password
        )
        conn.close()
        print("  PostgreSQL is ready ✅")
        break
    except psycopg2.OperationalError:
        print(f"  PostgreSQL not ready yet, retrying in 2s... ({i+1}/30)")
        time.sleep(2)
else:
    print("ERROR: PostgreSQL did not become ready in time.")
    exit(1)
EOF

# ── Check if data/raw/jobs.csv exists ───────────────────────
if [ ! -f "data/raw/jobs.csv" ]; then
    echo "ERROR: data/raw/jobs.csv not found!"
    echo "Please ensure jobs.csv is in the data/raw/ directory."
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
echo "  Starting dashboard at http://localhost:8050"
echo "============================================================"
python -m src.dashboard.app
