# Gunicorn 配置文件
import multiprocessing
import os
from config import API_CONFIG

# FastAPI 应用
application = "api.ml_api:app"

# 服务器套接字
bind = f"{API_CONFIG['host']}:{API_CONFIG['port']}"
backlog = 2048

# 工作进程
workers = multiprocessing.cpu_count() * 2 + 1  # 通常设置为 CPU 核心数的 2-4 倍
worker_class = "uvicorn.workers.UvicornWorker"  # 使用 Uvicorn Worker
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# 超时
timeout = 30
keepalive = 2

# 日志
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 进程命名
proc_name = 'ml_api_server'

# 服务器机制
daemon = False
pidfile = './gunicorn.pid'
user = None
group = None
tmp_upload_dir = None

# SSL
keyfile = None
certfile = None

# 调试
reload = False
reload_engine = "auto"