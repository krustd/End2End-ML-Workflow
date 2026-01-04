import os
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataProcessor:
    
    # 类级别的数据缓存，限制最大数量
    _data_cache = {}
    _max_cache_size = 3  # 每个进程最多保留3个数据副本
    
    def __init__(self):
        self.df = None
        self.data_file = None  # 添加属性跟踪当前加载的文件路径
        self.data_content = None  # 添加属性跟踪文件内容
        self.last_access_time = None  # 添加最后访问时间
        self.data_info = {
            'file_name': '',
            'file_size': 0,
            'rows_count': 0,
            'columns_count': 0,
            'columns': [],
            'numeric_columns': [],
            'categorical_columns': [],
            'target_column': '',
            'feature_columns': []
        }
        self.processed_data = None
        self.target_column = None
    
    def load_csv(self, file_content: str, filename: str = None) -> Dict[str, Any]:
        try:
            # 支持从内存中的文件内容加载
            import io
            
            file_size = len(file_content.encode('utf-8'))
            
            try:
                self.df = pd.read_csv(io.StringIO(file_content))
                self.data_content = file_content  # 保存文件内容
                self.data_file = filename  # 保存文件名
            except Exception as e:
                return {
                    'success': False,
                    'message': f'读取CSV内容失败: {str(e)}'
                }
            
            if self.df.empty:
                return {
                    'success': False,
                    'message': 'CSV文件为空'
                }
            
            self.data_info.update({
                'file_name': filename or 'unknown.csv',
                'file_size': file_size,
                'rows_count': len(self.df),
                'columns_count': len(self.df.columns),
                'columns': list(self.df.columns),
                'numeric_columns': list(self.df.select_dtypes(include=[np.number]).columns),
                'categorical_columns': list(self.df.select_dtypes(include=['object', 'category']).columns)
            })
            
            if self.data_info['numeric_columns']:
                self.data_info['target_column'] = self.data_info['numeric_columns'][0]
                self.target_column = self.data_info['target_column']
            
            self.data_info['feature_columns'] = [
                col for col in self.data_info['numeric_columns']
                if col != self.data_info['target_column']
            ]
            
            return {
                'success': True,
                'message': '数据加载成功',
                'data_info': self.data_info,
                'preview': self.get_data_preview(5)
            }
            
        except Exception as e:
            logger.error(f"加载CSV内容失败: {str(e)}")
            return {
                'success': False,
                'message': f'加载CSV内容失败: {str(e)}'
            }
    
    def load_csv_from_content(self, file_content: str, filename: str = None) -> Dict[str, Any]:
        """从文件内容加载CSV，使用缓存机制"""
        import io
        
        # 先尝试从缓存获取
        cached_data = self.get_from_cache(filename)
        if cached_data:
            self.df = cached_data['df']
            self.data_content = cached_data['data_content']
            self.data_file = filename
            self.data_info = cached_data['data_info'].copy()
            self.last_access_time = cached_data['last_access']
            return {
                'success': True,
                'message': '从缓存加载数据成功',
                'data_info': self.data_info,
                'preview': self.get_data_preview(5)
            }
        
        # 缓存中没有，从内容加载
        try:
            file_size = len(file_content.encode('utf-8'))
            
            try:
                self.df = pd.read_csv(io.StringIO(file_content))
                self.data_content = file_content
                self.data_file = filename
            except Exception as e:
                return {
                    'success': False,
                    'message': f'读取CSV内容失败: {str(e)}'
                }
            
            if self.df.empty:
                return {
                    'success': False,
                    'message': 'CSV内容为空'
                }
            
            self.data_info.update({
                'file_name': filename or 'unknown.csv',
                'file_size': file_size,
                'rows_count': len(self.df),
                'columns_count': len(self.df.columns),
                'columns': list(self.df.columns),
                'numeric_columns': list(self.df.select_dtypes(include=[np.number]).columns),
                'categorical_columns': list(self.df.select_dtypes(include=['object', 'category']).columns)
            })
            
            if self.data_info['numeric_columns']:
                self.data_info['target_column'] = self.data_info['numeric_columns'][0]
                self.target_column = self.data_info['target_column']
            
            self.data_info['feature_columns'] = [
                col for col in self.data_info['numeric_columns']
                if col != self.data_info['target_column']
            ]
            
            # 添加到缓存
            deleted_key = self.add_to_cache(filename, self.df.copy(), self.data_info.copy(), file_content)
            
            result = {
                'success': True,
                'message': '数据加载成功',
                'data_info': self.data_info,
                'preview': self.get_data_preview(5)
            }
            
            # 如果有旧数据被删除，添加到返回信息
            if deleted_key:
                result['message'] += f' (已清理旧数据: {deleted_key})'
            
            # 更新访问时间
            self.update_access_time()
            
            return result
            
        except Exception as e:
            logger.error(f"加载CSV内容失败: {str(e)}")
            return {
                'success': False,
                'message': f'加载CSV内容失败: {str(e)}'
            }
    
    def get_data_info(self) -> Dict[str, Any]:
        return self.data_info
    
    def get_data_preview(self, rows: int = 20) -> List[Dict[str, Any]]:
        if self.df is None:
            return []
        
        try:
            preview_df = self.df.head(rows)
            
            preview_data = []
            for _, row in preview_df.iterrows():
                row_dict = {}
                for col in preview_df.columns:
                    value = row[col]
                    if pd.isna(value):
                        row_dict[col] = None
                    elif isinstance(value, (np.integer, np.int64, np.int32)):
                        row_dict[col] = int(value)
                    elif isinstance(value, (np.floating, np.float64, np.float32)):
                        row_dict[col] = float(value)
                    elif isinstance(value, np.bool_):
                        row_dict[col] = bool(value)
                    else:
                        row_dict[col] = str(value) if value is not None else None
                preview_data.append(row_dict)
            
            return preview_data
            
        except Exception as e:
            logger.error(f"获取数据预览失败: {str(e)}")
            return []
    
    def preprocess_data(self, handle_missing: str = 'drop', target_column: Optional[str] = None) -> Tuple[pd.DataFrame, pd.Series]:
        if self.df is None:
            raise ValueError("没有加载的数据，请先调用load_csv方法")
        
        if target_column:
            self.target_column = target_column
            self.data_info['target_column'] = target_column
        
        if not self.target_column:
            raise ValueError("未指定目标列")
        
        if self.target_column not in self.df.columns:
            raise ValueError(f"目标列 '{self.target_column}' 不存在")
        
        df_processed = self.df.copy()
        
        if handle_missing == 'drop':
            df_processed = df_processed.dropna()
        elif handle_missing == 'mean':
            numeric_columns = df_processed.select_dtypes(include=[np.number]).columns
            df_processed[numeric_columns] = df_processed[numeric_columns].fillna(df_processed[numeric_columns].mean())
        elif handle_missing == 'median':
            numeric_columns = df_processed.select_dtypes(include=[np.number]).columns
            df_processed[numeric_columns] = df_processed[numeric_columns].fillna(df_processed[numeric_columns].median())
        elif handle_missing == 'mode':
            for col in df_processed.columns:
                mode_value = df_processed[col].mode()
                if not mode_value.empty:
                    df_processed[col] = df_processed[col].fillna(mode_value[0])
        
        y = df_processed[self.target_column]
        X = df_processed.drop(columns=[self.target_column])
        
        numeric_features = X.select_dtypes(include=[np.number]).columns
        X = X[numeric_features]
        
        self.data_info['feature_columns'] = list(numeric_features)
        
        self.processed_data = (X, y)
        
        return X, y
    
    def get_processed_data(self) -> Optional[Tuple[pd.DataFrame, pd.Series]]:
        return self.processed_data
    
    def set_target_column(self, column_name: str) -> bool:
        if self.df is None:
            return False
        
        if column_name not in self.df.columns:
            return False
        
        self.target_column = column_name
        self.data_info['target_column'] = column_name
        
        self.data_info['feature_columns'] = [
            col for col in self.data_info['numeric_columns']
            if col != column_name
        ]
        
        return True
    
    def get_column_statistics(self, column_name: str) -> Dict[str, Any]:
        if self.df is None or column_name not in self.df.columns:
            return {}
        
        column = self.df[column_name]
        
        stats = {
            'count': len(column) - column.isnull().sum(),
            'missing': column.isnull().sum(),
            'dtype': str(column.dtype)
        }
        
        if pd.api.types.is_numeric_dtype(column):
            stats.update({
                'mean': column.mean(),
                'std': column.std(),
                'min': column.min(),
                'max': column.max(),
                'q25': column.quantile(0.25),
                'q50': column.quantile(0.5),
                'q75': column.quantile(0.75)
            })
        
        elif pd.api.types.is_categorical_dtype(column) or column.dtype == 'object':
            stats.update({
                'unique': column.nunique(),
                'top': column.mode().iloc[0] if not column.mode().empty else None,
                'freq': column.value_counts().iloc[0] if not column.value_counts().empty else 0
            })
        
        return stats
    
    @classmethod
    def get_cache_key(cls, filename):
        """生成缓存键"""
        return filename or 'unknown'
    
    @classmethod
    def add_to_cache(cls, filename, df, data_info, data_content):
        """添加数据到缓存，如果超过限制则删除最旧的"""
        import time
        cache_key = cls.get_cache_key(filename)
        
        # 如果已存在，先删除旧的
        if cache_key in cls._data_cache:
            del cls._data_cache[cache_key]
        
        # 添加新数据
        cls._data_cache[cache_key] = {
            'df': df,
            'data_info': data_info,
            'data_content': data_content,
            'last_access': time.time()
        }
        
        # 如果超过限制，删除最旧的
        if len(cls._data_cache) > cls._max_cache_size:
            # 按访问时间排序，删除最旧的
            oldest_key = min(cls._data_cache.keys(),
                           key=lambda k: cls._data_cache[k]['last_access'])
            del cls._data_cache[oldest_key]
            return oldest_key
        return None
    
    @classmethod
    def get_from_cache(cls, filename):
        """从缓存获取数据并更新访问时间"""
        import time
        cache_key = cls.get_cache_key(filename)
        if cache_key in cls._data_cache:
            cls._data_cache[cache_key]['last_access'] = time.time()
            return cls._data_cache[cache_key]
        return None
    
    @classmethod
    def cleanup_cache(cls):
        """清理整个缓存"""
        cls._data_cache.clear()
    
    def update_access_time(self):
        """更新最后访问时间"""
        import time
        self.last_access_time = time.time()
    
    def check_and_cleanup(self, max_idle_time=1800):
        """检查并清理长时间未使用的数据（默认30分钟）"""
        import time
        if self.last_access_time and (time.time() - self.last_access_time) > max_idle_time:
            self.clear_data()
            return True
        return False
    
    def clear_data(self):
        """清理数据，释放内存"""
        self.df = None
        self.data_file = None
        self.data_content = None
        self.processed_data = None
        self.target_column = None
        self.last_access_time = None
        # 重置data_info但保留结构
        for key in self.data_info:
            if isinstance(self.data_info[key], list):
                self.data_info[key] = []
            elif isinstance(self.data_info[key], (int, float)):
                self.data_info[key] = 0
            else:
                self.data_info[key] = ''