#!/usr/bin/env python3
"""
启动脚本 - 用于启动机器学习数据分析与统计系统
支持单进程和多 Worker 模式
"""

import os
import sys
import argparse
import multiprocessing

def main():
    parser = argparse.ArgumentParser(description='启动机器学习数据分析与统计系统')
    parser.add_argument('--mode', choices=['single', 'multi'], default='multi',
                       help='启动模式: single (单进程) 或 multi (多 Worker)')
    parser.add_argument('--host', default='0.0.0.0', help='服务器主机地址')
    parser.add_argument('--port', type=int, default=8000, help='服务器端口')
    parser.add_argument('--workers', type=int, 
                       help=f'Worker 进程数量 (默认为 CPU 核心数 * 2 + 1, 即 {multiprocessing.cpu_count() * 2 + 1})')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("机器学习数据分析与统计系统")
    print("=" * 60)
    print(f"启动模式: {'多 Worker' if args.mode == 'multi' else '单进程'}")
    print(f"服务地址: http://{args.host}:{args.port}")
    print(f"调试模式: {'开启' if args.debug else '关闭'}")
    
    if args.mode == 'multi':
        workers = args.workers or (multiprocessing.cpu_count() * 2 + 1)
        print(f"Worker 进程数量: {workers}")
        
        # 使用 Gunicorn 启动多 Worker 模式
        cmd = [
            sys.executable, "-m", "gunicorn",
            "api.ml_api:app",
            "-c", "gunicorn_config.py",
            "--workers", str(workers),
            "--bind", f"{args.host}:{args.port}",
            "--worker-class", "uvicorn.workers.UvicornWorker"
        ]
        
        if args.debug:
            cmd.extend(["--log-level", "debug"])
            cmd.extend(["--reload"])
        
        print(f"启动命令: {' '.join(cmd)}")
        print("=" * 60)
        
        try:
            os.execvp(sys.executable, cmd)
        except Exception as e:
            print(f"启动失败: {str(e)}")
            sys.exit(1)
    else:
        # 使用 Uvicorn 启动单进程模式
        cmd = [
            sys.executable, "-m", "uvicorn",
            "api.ml_api:app",
            "--host", args.host,
            "--port", str(args.port)
        ]
        
        if args.debug:
            cmd.append("--reload")
        
        print(f"启动命令: {' '.join(cmd)}")
        print("=" * 60)
        
        try:
            os.execvp(sys.executable, cmd)
        except Exception as e:
            print(f"启动失败: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    main()