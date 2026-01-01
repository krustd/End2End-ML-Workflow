"""
数据处理模块
负责处理CSV数据的上传、验证和预处理
"""

import pandas as pd
import numpy as np
import os
from typing import Dict, List, Tuple, Any, Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataProcessor:
    """数据处理器类，负责数据的加载、验证和预处理"""
    
    def __init__(self):
        self.data = None
        self.data_info = {
            'file_name': None,
            'file_size': None,
            'rows_count': 0,
            'columns_count': 0,
            'columns': [],
            'numeric_columns': [],
            'categorical_columns': [],
            'target_column': None,
            'feature_columns': []
        }
    
    def load_csv(self, file_path: str, target_column: Optional[str] = None) -> Dict[str, Any]:
        """
        加载CSV文件
        
        Args:
            file_path: CSV文件路径
            target_column: 目标列名（可选）
            
        Returns:
            包含加载结果和数据的字典
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'message': f'文件不存在: {file_path}'
                }
            
            # 获取文件信息
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            file_name = os.path.basename(file_path)
            
            # 读取CSV文件
            self.data = pd.read_csv(file_path)
            
            # 更新数据信息
            self.data_info.update({
                'file_name': file_name,
                'file_size': round(file_size, 2),
                'rows_count': len(self.data),
                'columns_count': len(self.data.columns),
                'columns': list(self.data.columns),
                'numeric_columns': list(self.data.select_dtypes(include=[np.number]).columns),
                'categorical_columns': list(self.data.select_dtypes(include=['object', 'category']).columns)
            })
            
            # 设置目标列和特征列
            if target_column and target_column in self.data.columns:
                self.data_info['target_column'] = target_column
                self.data_info['feature_columns'] = [col for col in self.data.columns if col != target_column]
            elif target_column:
                return {
                    'success': False,
                    'message': f'指定的目标列 "{target_column}" 不存在于数据中'
                }
            
            logger.info(f"成功加载数据: {file_name}, 行数: {self.data_info['rows_count']}, 列数: {self.data_info['columns_count']}")
            
            return {
                'success': True,
                'message': '数据加载成功',
                'data_info': self.data_info,
                'preview': self.data.head(20).to_dict('records')
            }
            
        except Exception as e:
            logger.error(f"加载数据时出错: {str(e)}")
            return {
                'success': False,
                'message': f'加载数据时出错: {str(e)}'
            }
    
    def validate_data(self) -> Dict[str, Any]:
        """
        验证数据质量
        
        Returns:
            包含验证结果的字典
        """
        if self.data is None:
            return {
                'success': False,
                'message': '没有加载的数据'
            }
        
        validation_results = {
            'missing_values': {},
            'data_types': {},
            'summary': {}
        }
        
        # 检查缺失值
        missing_values = self.data.isnull().sum()
        validation_results['missing_values'] = missing_values[missing_values > 0].to_dict()
        
        # 检查数据类型
        validation_results['data_types'] = self.data.dtypes.astype(str).to_dict()
        
        # 数据摘要
        validation_results['summary'] = {
            'total_rows': len(self.data),
            'total_columns': len(self.data.columns),
            'numeric_columns': len(self.data_info['numeric_columns']),
            'categorical_columns': len(self.data_info['categorical_columns']),
            'has_missing_values': len(validation_results['missing_values']) > 0
        }
        
        return {
            'success': True,
            'validation_results': validation_results
        }
    
    def preprocess_data(self, handle_missing: str = 'drop', target_column: Optional[str] = None) -> Tuple[pd.DataFrame, pd.Series]:
        """
        预处理数据
        
        Args:
            handle_missing: 处理缺失值的方法 ('drop', 'mean', 'median', 'mode')
            target_column: 目标列名
            
        Returns:
            处理后的特征数据和目标数据
        """
        if self.data is None:
            raise ValueError('没有加载的数据')
        
        # 复制数据以避免修改原始数据
        processed_data = self.data.copy()
        
        # 设置目标列
        if target_column:
            self.data_info['target_column'] = target_column
        elif not self.data_info['target_column'] and self.data_info['numeric_columns']:
            # 如果没有指定目标列，默认使用第一个数值列作为目标列
            self.data_info['target_column'] = self.data_info['numeric_columns'][0]
        
        target_col = self.data_info['target_column']
        if not target_col:
            raise ValueError('没有指定目标列，且数据中没有数值列')
        
        # 分离特征和目标
        feature_cols = [col for col in processed_data.columns if col != target_col]
        self.data_info['feature_columns'] = feature_cols
        
        # 处理缺失值
        if handle_missing == 'drop':
            processed_data = processed_data.dropna()
        elif handle_missing == 'mean':
            for col in self.data_info['numeric_columns']:
                if col in processed_data.columns and processed_data[col].isnull().any():
                    processed_data[col].fillna(processed_data[col].mean(), inplace=True)
        elif handle_missing == 'median':
            for col in self.data_info['numeric_columns']:
                if col in processed_data.columns and processed_data[col].isnull().any():
                    processed_data[col].fillna(processed_data[col].median(), inplace=True)
        elif handle_missing == 'mode':
            for col in processed_data.columns:
                if processed_data[col].isnull().any():
                    mode_val = processed_data[col].mode()
                    if len(mode_val) > 0:
                        processed_data[col].fillna(mode_val[0], inplace=True)
        
        # 处理分类变量 - 独热编码
        categorical_cols = self.data_info['categorical_columns']
        if categorical_cols:
            processed_data = pd.get_dummies(processed_data, columns=categorical_cols, drop_first=True)
        
        # 更新特征列（独热编码后可能发生变化）
        feature_cols = [col for col in processed_data.columns if col != target_col]
        self.data_info['feature_columns'] = feature_cols
        
        # 分离特征和目标
        X = processed_data[feature_cols]
        y = processed_data[target_col]
        
        logger.info(f"数据预处理完成，特征数: {len(feature_cols)}, 样本数: {len(X)}")
        
        return X, y
    
    def get_data_info(self) -> Dict[str, Any]:
        """获取数据信息"""
        return self.data_info
    
    def get_data_preview(self, n_rows: int = 20) -> List[Dict[str, Any]]:
        """
        获取数据预览
        
        Args:
            n_rows: 预览行数
            
        Returns:
            数据预览列表
        """
        if self.data is None:
            return []
        
        return self.data.head(n_rows).to_dict('records')