"""
数据处理器模块
负责CSV数据的加载、预处理和分析
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataProcessor:
    """数据处理器类"""
    
    def __init__(self):
        """初始化数据处理器"""
        self.df = None
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
    
    def load_csv(self, file_path: str) -> Dict[str, Any]:
        """
        加载CSV文件
        
        Args:
            file_path: CSV文件路径
            
        Returns:
            加载结果字典，包含success、message和data_info等信息
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'message': f'文件不存在: {file_path}'
                }
            
            # 获取文件信息
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            
            # 读取CSV文件
            try:
                self.df = pd.read_csv(file_path)
            except Exception as e:
                return {
                    'success': False,
                    'message': f'读取CSV文件失败: {str(e)}'
                }
            
            # 检查数据是否为空
            if self.df.empty:
                return {
                    'success': False,
                    'message': 'CSV文件为空'
                }
            
            # 更新数据信息
            self.data_info.update({
                'file_name': file_name,
                'file_size': file_size,
                'rows_count': len(self.df),
                'columns_count': len(self.df.columns),
                'columns': list(self.df.columns),
                'numeric_columns': list(self.df.select_dtypes(include=[np.number]).columns),
                'categorical_columns': list(self.df.select_dtypes(include=['object', 'category']).columns)
            })
            
            # 如果有数值列，默认将第一个数值列设为目标列
            if self.data_info['numeric_columns']:
                self.data_info['target_column'] = self.data_info['numeric_columns'][0]
                self.target_column = self.data_info['target_column']
            
            # 将其他数值列设为特征列
            self.data_info['feature_columns'] = [
                col for col in self.data_info['numeric_columns'] 
                if col != self.data_info['target_column']
            ]
            
            return {
                'success': True,
                'message': '数据加载成功',
                'data_info': self.data_info,
                'preview': self.get_data_preview(5)  # 返回前5行作为预览
            }
            
        except Exception as e:
            logger.error(f"加载CSV文件失败: {str(e)}")
            return {
                'success': False,
                'message': f'加载CSV文件失败: {str(e)}'
            }
    
    def get_data_info(self) -> Dict[str, Any]:
        """
        获取数据信息
        
        Returns:
            数据信息字典
        """
        return self.data_info
    
    def get_data_preview(self, rows: int = 20) -> List[Dict[str, Any]]:
        """
        获取数据预览
        
        Args:
            rows: 预览行数
            
        Returns:
            预览数据列表
        """
        if self.df is None:
            return []
        
        try:
            # 获取前n行数据
            preview_df = self.df.head(rows)
            
            # 转换为字典列表
            preview_data = []
            for _, row in preview_df.iterrows():
                # 处理NaN值，转换为None
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
        """
        预处理数据
        
        Args:
            handle_missing: 处理缺失值的方法 ('drop', 'mean', 'median', 'mode')
            target_column: 目标列名
            
        Returns:
            特征DataFrame和目标Series的元组
        """
        if self.df is None:
            raise ValueError("没有加载的数据，请先调用load_csv方法")
        
        # 设置目标列
        if target_column:
            self.target_column = target_column
            self.data_info['target_column'] = target_column
        
        if not self.target_column:
            raise ValueError("未指定目标列")
        
        # 检查目标列是否存在
        if self.target_column not in self.df.columns:
            raise ValueError(f"目标列 '{self.target_column}' 不存在")
        
        # 复制原始数据
        df_processed = self.df.copy()
        
        # 处理缺失值
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
        
        # 分离特征和目标
        y = df_processed[self.target_column]
        X = df_processed.drop(columns=[self.target_column])
        
        # 只保留数值特征
        numeric_features = X.select_dtypes(include=[np.number]).columns
        X = X[numeric_features]
        
        # 更新特征列信息
        self.data_info['feature_columns'] = list(numeric_features)
        
        # 保存处理后的数据
        self.processed_data = (X, y)
        
        return X, y
    
    def get_processed_data(self) -> Optional[Tuple[pd.DataFrame, pd.Series]]:
        """
        获取处理后的数据
        
        Returns:
            特征DataFrame和目标Series的元组，如果没有处理过数据则返回None
        """
        return self.processed_data
    
    def set_target_column(self, column_name: str) -> bool:
        """
        设置目标列
        
        Args:
            column_name: 列名
            
        Returns:
            是否设置成功
        """
        if self.df is None:
            return False
        
        if column_name not in self.df.columns:
            return False
        
        self.target_column = column_name
        self.data_info['target_column'] = column_name
        
        # 更新特征列
        self.data_info['feature_columns'] = [
            col for col in self.data_info['numeric_columns'] 
            if col != column_name
        ]
        
        return True
    
    def get_column_statistics(self, column_name: str) -> Dict[str, Any]:
        """
        获取列的统计信息
        
        Args:
            column_name: 列名
            
        Returns:
            统计信息字典
        """
        if self.df is None or column_name not in self.df.columns:
            return {}
        
        column = self.df[column_name]
        
        stats = {
            'count': len(column) - column.isnull().sum(),
            'missing': column.isnull().sum(),
            'dtype': str(column.dtype)
        }
        
        # 如果是数值列，添加数值统计
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
        
        # 如果是分类列，添加分类统计
        elif pd.api.types.is_categorical_dtype(column) or column.dtype == 'object':
            stats.update({
                'unique': column.nunique(),
                'top': column.mode().iloc[0] if not column.mode().empty else None,
                'freq': column.value_counts().iloc[0] if not column.value_counts().empty else 0
            })
        
        return stats