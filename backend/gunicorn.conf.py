import multiprocessing
import os

# 并发配置
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gunicorn.workers.gthread.GThreadWorker'
threads = 4

# 端口配置
bind = '0.0.0.0:8000'
backlog = 2048

# 超时配置
timeout = 120
keepalive = 2

# 进程管理
max_requests = 1000
max_requests_jitter = 100
preload_app = True

# 日志配置
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)
accesslog = os.path.join(log_dir, 'access.log')
errorlog = os.path.join(log_dir, 'error.log')
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# 资源限制
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190