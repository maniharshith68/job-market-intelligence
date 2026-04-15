FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

RUN apt-get update && apt-get install -y \
    gcc g++ libpq-dev curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

RUN pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl

# Copy full project
COPY . .

# Create directories
RUN mkdir -p logs data/processed data/raw

# ── PRE-PROCESS DATA AT BUILD TIME ──────────────────────────
# This runs ingestion + NLP + NER during docker build
# So processed CSVs are baked into the image
# No timeout issues at deploy time
RUN if [ -f "data/raw/jobs.csv" ]; then \
    echo "Running ingestion pipeline..." && \
    python -m src.ingestion.run_ingestion && \
    echo "Running NLP pipeline..." && \
    python -m src.nlp.run_nlp && \
    echo "Running NER pipeline..." && \
    python -m src.nlp.run_ner && \
    echo "Data preprocessing complete ✅"; \
    else \
    echo "WARNING: data/raw/jobs.csv not found, skipping preprocessing"; \
    fi

RUN chmod +x scripts/entrypoint.sh

EXPOSE 8050

ENTRYPOINT ["scripts/entrypoint.sh"]
