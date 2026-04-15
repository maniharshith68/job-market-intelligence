# gunicorn_config.py
bind = "0.0.0.0:8050"
workers = 1
timeout = 1200        # 20 min timeout for pipeline
worker_class = "sync"
