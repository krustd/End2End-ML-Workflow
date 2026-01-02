import os
import sys
import argparse
import logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api import run_api
from config import API_CONFIG

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='机器学习数据分析与统计系统')
    parser.add_argument('--host', default=API_CONFIG['host'], help='服务器主机地址')
    parser.add_argument('--port', type=int, default=API_CONFIG['port'], help='服务器端口')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    
    args = parser.parse_args()
    
    logger.info(f"启动机器学习数据分析与统计系统")
    logger.info(f"服务地址: http://{args.host}:{args.port}")
    logger.info(f"调试模式: {'开启' if args.debug else '关闭'}")
    
    os.makedirs("saved_models", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    try:
        run_api(host=args.host, port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        logger.info("服务已停止")
    except Exception as e:
        logger.error(f"服务启动失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()