"""
机器学习数据分析与统计系统
"""

from .data import DataProcessor
from .models import ModelTrainer, Predictor
from .api import app, run_api
from .config import (
    MODEL_CONFIG,
    DATA_CONFIG,
    API_CONFIG,
    PREDICTION_CONFIG,
    SYSTEM_CONFIG,
    LOGGING_CONFIG,
    DATABASE_CONFIG
)

__version__ = "1.0.0"
__title__ = "机器学习数据分析与统计系统"
__description__ = "基于机器学习的数据分析与统计系统"

__all__ = [
    'DataProcessor',
    'ModelTrainer',
    'Predictor',
    'app',
    'run_api',
    'MODEL_CONFIG',
    'DATA_CONFIG',
    'API_CONFIG',
    'PREDICTION_CONFIG',
    'SYSTEM_CONFIG',
    'LOGGING_CONFIG',
    'DATABASE_CONFIG'
]