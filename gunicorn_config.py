# gunicorn_config.py
bind = "0.0.0.0:8050"
workers = 1
timeout = 120
worker_class = "sync"
