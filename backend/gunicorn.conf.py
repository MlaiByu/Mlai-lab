import multiprocessing
import os

# 并发配置 - 针对50+并发用户优化
workers = min(multiprocessing.cpu_count() * 2 + 1, 12)
worker_class = 'gunicorn.workers.gthread.GThreadWorker'
threads = 8
worker_connections = 1000

# 端口配置
bind = '0.0.0.0:8000'
backlog = 2048

# 超时配置 - 适应容器启动时间
timeout = 300
graceful_timeout = 60
keepalive = 60

# 进程管理 - 防止内存泄漏
max_requests = 500
max_requests_jitter = 50
preload_app = False
reload = True

# 日志配置
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'log')
os.makedirs(log_dir, exist_ok=True)
accesslog = os.path.join(log_dir, 'gunicorn_access.log')
errorlog = os.path.join(log_dir, 'gunicorn_error.log')
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 资源限制
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# 统计配置（已禁用，需要时启用）
# statsd_host = 'localhost:8125'
