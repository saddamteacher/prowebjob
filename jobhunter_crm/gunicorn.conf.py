"""Gunicorn configuration for JobHunter CRM."""
import multiprocessing, os

bind         = "unix:/run/gunicorn.sock"
workers      = min(multiprocessing.cpu_count() * 2 + 1, 9)
worker_class = "sync"
timeout      = 120
keepalive    = 5
max_requests = 1000
max_requests_jitter = 100

# Logging
log_dir   = os.getenv('LOG_DIR', '/app/logs')
accesslog = f"{log_dir}/gunicorn_access.log"
errorlog  = f"{log_dir}/gunicorn_error.log"
loglevel  = os.getenv('LOG_LEVEL', 'info').lower()

# Process naming
proc_name = "jobhunter-crm"
