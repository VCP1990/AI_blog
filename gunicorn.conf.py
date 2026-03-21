import os

bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
timeout = 30
keepalive = 2
spew = False

accesslog = "-"
errorlog = "-"
loglevel = "info"

raw_env = ["DJANGO_ENVIRONMENT=production"]
