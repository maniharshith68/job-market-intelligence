# src/nlp/skills_vocabulary.py

SKILLS_VOCABULARY = {
    "programming_languages": [
        "Python", "Java", "JavaScript", "TypeScript", "C", "C++", "C#",
        "R", "Go", "Rust", "Scala", "Kotlin", "Swift", "Ruby", "PHP",
        "MATLAB", "Shell", "Bash", "Perl", "Haskell", "Lua"
    ],
    "web_frameworks": [
        "React", "Angular", "Vue", "Node.js", "Django", "Flask", "FastAPI",
        "Spring", "Express", "Next.js", "Nuxt.js", "Rails", "Laravel",
        "ASP.NET", "Svelte", "Bootstrap", "Tailwind"
    ],
    "data_and_ml": [
        "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "XGBoost",
        "LightGBM", "Pandas", "NumPy", "SciPy", "Hugging Face",
        "OpenCV", "NLTK", "spaCy", "Transformers", "LangChain",
        "MLflow", "Kubeflow", "Airflow", "Spark", "Hadoop",
        "machine learning", "deep learning", "natural language processing",
        "computer vision", "reinforcement learning", "data science",
        "data analysis", "data engineering", "feature engineering",
        "model deployment", "A/B testing", "statistical modeling"
    ],
    "databases": [
        "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch",
        "Cassandra", "DynamoDB", "SQLite", "Oracle", "Microsoft SQL Server",
        "Neo4j", "InfluxDB", "Snowflake", "BigQuery", "Redshift", "dbt"
    ],
    "cloud_and_devops": [
        "AWS", "Azure", "GCP", "Google Cloud", "Docker", "Kubernetes",
        "Terraform", "Ansible", "Jenkins", "CI/CD", "GitHub Actions",
        "CircleCI", "Helm", "Prometheus", "Grafana", "Datadog",
        "Linux", "Unix", "Nginx", "Apache", "microservices",
        "serverless", "cloud computing", "DevOps", "MLOps", "DataOps"
    ],
    "data_visualization": [
        "Tableau", "Power BI", "Looker", "Plotly", "Matplotlib",
        "Seaborn", "D3.js", "Grafana", "Kibana", "Excel", "Dash"
    ],
    "tools_and_platforms": [
        "Git", "GitHub", "GitLab", "Bitbucket", "Jira", "Confluence",
        "Slack", "VS Code", "IntelliJ", "Jupyter", "Databricks",
        "Kafka", "RabbitMQ", "Celery", "REST", "GraphQL", "gRPC",
        "API", "Postman", "Swagger", "OpenAPI"
    ],
    "soft_skills": [
        "communication", "leadership", "teamwork", "collaboration",
        "problem solving", "critical thinking", "project management",
        "agile", "scrum", "kanban", "time management", "mentoring",
        "cross-functional", "stakeholder management", "presentation"
    ],
    "business_and_domain": [
        "product management", "business analysis", "data governance",
        "risk management", "compliance", "fintech", "healthcare",
        "e-commerce", "cybersecurity", "blockchain", "IoT",
        "quantitative analysis", "financial modeling", "marketing analytics"
    ]
}


def get_all_skills() -> list:
    """Return a flat list of all skills across all categories."""
    all_skills = []
    for category, skills in SKILLS_VOCABULARY.items():
        all_skills.extend(skills)
    return all_skills


def get_skill_category(skill: str) -> str:
    """Return the category for a given skill."""
    skill_lower = skill.lower()
    for category, skills in SKILLS_VOCABULARY.items():
        if any(s.lower() == skill_lower for s in skills):
            return category
    return "other"
