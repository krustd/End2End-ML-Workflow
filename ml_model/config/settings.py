import os
from typing import Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_CONFIG = {
    "default_model": "linear_regression",
    "model_dir": os.path.join(BASE_DIR, "saved_models"),
    "supported_models": [
        "linear_regression",
        "ridge",
        "lasso",
        "elastic_net",
        "random_forest",
        "gradient_boosting",
        "svr",
        "decision_tree",
        "knn"
    ]
}

DATA_CONFIG = {
    "upload_dir": os.path.join(BASE_DIR, "uploads"),
    "supported_formats": [".csv"],
    "max_file_size": 100 * 1024 * 1024,
    "preview_rows": 20
}

API_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "debug": False,
    "cors_origins": ["*"],
    "title": "机器学习数据分析与统计系统",
    "description": "基于机器学习的数据分析与统计系统API",
    "version": "1.0.0"
}

PREDICTION_CONFIG = {
    "batch_size": 100,
    "export_formats": ["csv", "excel", "json"],
    "default_export_format": "csv"
}

SYSTEM_CONFIG = {
    "name": "机器学习数据分析与统计系统",
    "version": "1.0.0",
    "description": "基于机器学习的数据分析与统计系统",
    "disclaimer": "预测结果仅供参考，不构成决策建议"
}

LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": os.path.join(BASE_DIR, "logs", "ml_system.log")
}

DATABASE_CONFIG = {
    "url": "sqlite:///ml_system.db",
    "echo": False
}