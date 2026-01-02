import os
import json
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def ensure_dir(directory: str) -> None:
    if not os.path.exists(directory):
        os.makedirs(directory)


def save_json(data: Dict[str, Any], file_path: str) -> bool:
    try:
        ensure_dir(os.path.dirname(file_path))
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"保存JSON文件失败: {str(e)}")
        return False


def load_json(file_path: str) -> Optional[Dict[str, Any]]:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"加载JSON文件失败: {str(e)}")
        return None


def validate_csv_file(file_path: str) -> Dict[str, Any]:
    try:
        if not os.path.exists(file_path):
            return {
                'valid': False,
                'message': '文件不存在'
            }
        
        if not file_path.lower().endswith('.csv'):
            return {
                'valid': False,
                'message': '文件格式不支持，请上传CSV文件'
            }
        
        df = pd.read_csv(file_path, nrows=5)
        
        if df.empty:
            return {
                'valid': False,
                'message': '文件为空或没有有效数据'
            }
        
        return {
            'valid': True,
            'message': '文件验证通过',
            'columns': list(df.columns),
            'shape': df.shape
        }
        
    except Exception as e:
        return {
            'valid': False,
            'message': f'文件验证失败: {str(e)}'
        }


def format_metrics(metrics: Dict[str, float]) -> Dict[str, str]:
    formatted = {}
    for key, value in metrics.items():
        if isinstance(value, float):
            formatted[key] = f"{value:.4f}"
        else:
            formatted[key] = str(value)
    return formatted


def generate_model_summary(model_metrics: Dict[str, Any]) -> Dict[str, Any]:
    test_metrics = model_metrics.get('test_metrics', {})
    cv_scores = model_metrics.get('cv_scores', {})
    
    return {
        'model_type': model_metrics.get('model_type', 'Unknown'),
        'r2_score': test_metrics.get('r2', 0),
        'rmse': test_metrics.get('rmse', 0),
        'mae': test_metrics.get('mae', 0),
        'cv_mean': cv_scores.get('mean', 0),
        'cv_std': cv_scores.get('std', 0),
        'feature_count': len(model_metrics.get('feature_names', [])),
        'target_name': model_metrics.get('target_name', 'Unknown')
    }


def create_prediction_report(predictions: List[Dict[str, Any]], 
                           input_data: List[Dict[str, Any]], 
                           model_info: Dict[str, Any]) -> Dict[str, Any]:
    report = {
        'title': '预测结果报告',
        'model_info': model_info,
        'prediction_count': len(predictions),
        'predictions': []
    }
    
    for i, (pred, input_item) in enumerate(zip(predictions, input_data)):
        report['predictions'].append({
            'index': i + 1,
            'input': input_item,
            'prediction': pred
        })
    
    return report


def calculate_feature_importance(model, feature_names: List[str]) -> Dict[str, float]:
    try:
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            return dict(zip(feature_names, importances))
        elif hasattr(model, 'coef_'):
            coef = model.coef_
            if len(coef.shape) > 1:
                coef = coef[0]
            return dict(zip(feature_names, np.abs(coef)))
        else:
            return {}
    except Exception as e:
        logger.error(f"计算特征重要性失败: {str(e)}")
        return {}


def detect_outliers(df: pd.DataFrame, column: str, method: str = 'iqr') -> List[int]:
    try:
        if method == 'iqr':
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)].index.tolist()
        elif method == 'zscore':
            z_scores = np.abs((df[column] - df[column].mean()) / df[column].std())
            outliers = df[z_scores > 3].index.tolist()
        else:
            outliers = []
        
        return outliers
    except Exception as e:
        logger.error(f"检测异常值失败: {str(e)}")
        return []


def generate_data_profile(df: pd.DataFrame) -> Dict[str, Any]:
    profile = {
        'shape': df.shape,
        'columns': list(df.columns),
        'dtypes': df.dtypes.astype(str).to_dict(),
        'missing_values': df.isnull().sum().to_dict(),
        'numeric_summary': {},
        'categorical_summary': {}
    }
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        profile['numeric_summary'][col] = {
            'count': df[col].count(),
            'mean': df[col].mean(),
            'std': df[col].std(),
            'min': df[col].min(),
            'max': df[col].max(),
            'q25': df[col].quantile(0.25),
            'q50': df[col].quantile(0.5),
            'q75': df[col].quantile(0.75)
        }
    
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    for col in categorical_cols:
        profile['categorical_summary'][col] = {
            'count': df[col].count(),
            'unique': df[col].nunique(),
            'top': df[col].mode().iloc[0] if not df[col].mode().empty else None,
            'freq': df[col].value_counts().iloc[0] if not df[col].value_counts().empty else 0
        }
    
    return profile


def safe_float_conversion(value: Any) -> Optional[float]:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def safe_int_conversion(value: Any) -> Optional[int]:
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def truncate_string(text: str, max_length: int = 50) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def serialize_numpy_pandas(obj: Any) -> Any:
    if obj is None:
        return None
    
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Series):
        return obj.to_dict()
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict()
    elif isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    elif isinstance(obj, pd.Timedelta):
        return str(obj)
    elif str(type(obj)).startswith("<class 'numpy.dtypes"):
        return str(obj)
    elif hasattr(obj, 'dtype'):
        dtype_str = str(obj.dtype)
        if dtype_str.startswith('float'):
            return float(obj) if hasattr(obj, 'item') else str(obj)
        elif dtype_str.startswith('int'):
            return int(obj) if hasattr(obj, 'item') else str(obj)
        else:
            return str(obj)
    elif isinstance(obj, dict):
        return {key: serialize_numpy_pandas(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [serialize_numpy_pandas(item) for item in obj]
    else:
        return obj