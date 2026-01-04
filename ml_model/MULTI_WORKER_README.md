# FastAPI 多 Worker 模式配置

本项目已配置支持使用 Gunicorn + Uvicorn 的多 Worker 模式，可以处理来自 GoFrame 的并发请求。

## 启动方式

### 1. 使用 main.py 启动（推荐）

```bash
# 默认启动多 Worker 模式
uv run main.py

# 指定 Worker 数量
uv run main.py --workers 4

# 启动单进程模式
uv run main.py --mode single

# 启动调试模式
uv run main.py --debug

# 指定主机和端口
uv run main.py --host 0.0.0.0 --port 8000
```

### 2. 使用 run.py 启动

```bash
# 使用 Gunicorn 启动多 Worker 模式
uv run run.py --use-gunicorn

# 指定 Worker 数量
uv run run.py --use-gunicorn --workers 4
```

### 3. 直接使用 Gunicorn

```bash
uv run gunicorn -c gunicorn_config.py api.ml_api:app
```

## 配置说明

### Gunicorn 配置文件 (gunicorn_config.py)

- **Worker 数量**: 默认为 CPU 核心数 × 2 + 1
- **Worker 类型**: uvicorn.workers.UvicornWorker
- **最大请求数**: 1000（防止内存泄漏）
- **请求抖动**: 50（避免所有 Worker 同时重启）

### 多 Worker 模式的工作原理

1. Gunicorn 作为主进程，管理多个 Worker 进程
2. 每个 Worker 进程都是一个独立的 Uvicorn 实例
3. 当 GoFrame 发送 4 个并发请求时，Gunicorn 会自动将它们分配给不同的 Worker 进程
4. 每个 Worker 可以独立处理请求，互不干扰

## 测试并发请求

使用提供的测试脚本验证多 Worker 模式：

```bash
# 安装 aiohttp（如果尚未安装）
uv add aiohttp

# 运行并发测试
uv run test_concurrent.py --requests 10
```

## 注意事项

1. **状态共享**: 多 Worker 进程之间不共享内存，如果有全局状态需要考虑使用外部存储（如 Redis）
2. **文件上传**: 文件上传功能在多 Worker 模式下需要确保所有 Worker 都能访问上传的文件
3. **日志**: 日志会输出到标准输出，由 Gunicorn 统一管理
4. **调试**: 在多 Worker 模式下，调试较为困难，建议在开发时使用单进程模式

## 性能调优

1. **Worker 数量**: 通常设置为 CPU 核心数的 2-4 倍
2. **最大请求数**: 根据内存使用情况调整，防止内存泄漏
3. **超时设置**: 根据业务需求调整请求超时时间

## 故障排除

如果遇到问题，可以尝试：

1. 检查日志输出，查看是否有错误信息
2. 使用单进程模式验证应用是否正常工作
3. 减少 Worker 数量，观察是否是资源不足导致的问题
4. 检查端口是否被占用