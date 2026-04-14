# 🧠 Job Market Intelligence Platform

> An end-to-end NLP analytics platform that ingests job descriptions, extracts in-demand skills via BERTopic & NER, and surfaces real-time market insights through an interactive Plotly Dash dashboard powered by LLM-based resume scoring.

---

## 📌 Project Overview

This platform analyzes 1,200+ real-world job descriptions to identify skill trends, topic clusters, and keyword patterns in the job market. It features an AI-powered resume scorer that evaluates candidate fit against any job description using Llama 3.3 70B via Groq.

---

## 🏗️ Architecture

jobs.csv (raw data)
↓
┌─────────────────────────────────────────────────┐
│              Data Ingestion Pipeline             │
│   pandas • spaCy • text cleaning • lemmatization │
└───────────────────────┬─────────────────────────┘
↓
┌─────────────────────────────────────────────────┐
│                 NLP Pipeline                     │
│        TF-IDF • BERTopic • NER • PhraseMatcher   │
└───────────────────────┬─────────────────────────┘
↓
┌─────────────────────────────────────────────────┐
│              PostgreSQL Database                 │
│   job_postings • top_skills • keyword_trends     │
│   skill_extractions • topic_assignments          │
└───────────────────────┬─────────────────────────┘
↓
┌─────────────────────────────────────────────────┐
│           Plotly Dash Dashboard                  │
│  Skill Intelligence • Keyword Trends             │
│  Topic Explorer • AI Resume Scorer               │
└─────────────────────────────────────────────────┘

---

## ✨ Features

- **NLP Ingestion Pipeline** — Cleans, lemmatizes, and processes 1,200+ job descriptions
- **TF-IDF Extraction** — Identifies top keywords across the entire job corpus
- **BERTopic Modeling** — Discovers latent topic clusters in job descriptions
- **NER Skill Extraction** — Extracts 500+ unique skills using spaCy PhraseMatcher
- **PostgreSQL Storage** — Stores all structured outputs with SQLAlchemy ORM
- **Interactive Dashboard** — 4-tab Plotly Dash app with live DB queries
- **AI Resume Scorer** — Llama 3.3 70B (via Groq) scores resume-to-job fit with matched/missing skills and actionable suggestions

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| NLP | spaCy, BERTopic, scikit-learn, sentence-transformers |
| Database | PostgreSQL 15, SQLAlchemy |
| Dashboard | Plotly Dash, Dash Bootstrap Components |
| LLM | Llama 3.3 70B via Groq API |
| Containerization | Docker, Docker Compose |
| Deployment | Render.com + Supabase |

---

## 📁 Project Structure

job-market-intelligence/
├── config/                  # YAML configuration
├── data/
│   ├── raw/                 # Input: jobs.csv (not committed)
│   └── processed/           # Pipeline outputs (not committed)
├── src/
│   ├── ingestion/           # Data loading & preprocessing
│   ├── nlp/                 # TF-IDF, BERTopic, NER modules
│   ├── database/            # PostgreSQL models & inserters
│   ├── dashboard/           # Plotly Dash app & callbacks
│   └── llm/                 # Resume scorer (Groq + Llama)
├── scripts/
│   └── entrypoint.sh        # Docker startup script
├── logs/                    # Rotating log files (not committed)
├── tests/                   # Unit tests
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11
- Docker & Docker Compose
- Groq API key (free at https://console.groq.com)

### Option 1 — Docker (Recommended)

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/job-market-intelligence.git
cd job-market-intelligence

# 2. Set up environment
cp .env.example .env
# Edit .env and fill in your GROQ_API_KEY and DB credentials

# 3. Add your dataset
mkdir -p data/raw
cp /path/to/your/jobs.csv data/raw/jobs.csv

# 4. Run everything
docker compose up --build
```

Visit `http://localhost:8050` 🎉

---

### Option 2 — Local Development

```bash
# 1. Clone and enter repo
git clone https://github.com/yourusername/job-market-intelligence.git
cd job-market-intelligence

# 2. Create virtual environment with Python 3.11
~/.pyenv/versions/3.11.9/bin/python -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 4. Set up environment
cp .env.example .env
# Edit .env with your credentials

# 5. Start PostgreSQL
docker run --name jobmarket-pg \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=admin123 \
  -e POSTGRES_DB=jobmarket \
  -p 5432:5432 -d postgres:15

# 6. Add your dataset
mkdir -p data/raw
cp /path/to/jobs.csv data/raw/jobs.csv

# 7. Run pipelines
python -m src.ingestion.run_ingestion
python -m src.nlp.run_nlp
python -m src.nlp.run_ner
python -m src.database.run_database

# 8. Launch dashboard
python -m src.dashboard.app
```

---

## 📊 Dashboard Preview

| Tab | Description |
|---|---|
| 🔥 Skill Intelligence | Top skills bar chart + category breakdown donut |
| 📈 Keyword Trends | Treemap + top 50 keywords table |
| 🧠 Topic Explorer | BERTopic cluster distribution |
| 🤖 Resume Scorer | AI-powered resume fit scoring with feedback |

---

## 🔑 Environment Variables

Copy `.env.example` to `.env` and configure:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=jobmarket
POSTGRES_USER=admin
POSTGRES_PASSWORD=yourpassword
GROQ_API_KEY=your_groq_key_here
APP_ENV=development
```
---

## Collaboration
This project was developed in collaboration with [Shruti Kumari](https://github.com/shrutisurya108).
 
## Acknowledgements
This project was built in collaboration with [Shruti Kumari](https://github.com/shrutisurya108).
 
## 👤 Authors
- [Harshith Bhattaram](https://github.com/maniharshith68)
- [Shruti Kumari](https://github.com/shrutisurya108)
 
Built with ❤️ as a production-grade data science portfolio project.
